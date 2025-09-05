# ruff: noqa: UP006 UP007 UP045
import errno
import logging
import os
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.logs.modules import get_module_logger

from .configs import ProcessConfig
from .configs import ServerConfig
from .events import EventCallbacks
from .events import ProcessCommunicationEvent
from .events import ProcessLogStderrEvent
from .events import ProcessLogStdoutEvent
from .events import ProcessOutputChannel
from .types import Process
from .types import ProcessDispatcher
from .types import ProcessInputDispatcher
from .types import ProcessOutputDispatcher
from .utils.diag import compact_traceback
from .utils.fds import read_fd
from .utils.ostypes import Fd
from .utils.strings import as_bytes
from .utils.strings import find_prefix_at_end
from .utils.strings import strip_escapes


log = get_module_logger(globals())  # noqa


##


class BaseProcessDispatcherImpl(ProcessDispatcher, Abstract):
    def __init__(
            self,
            process: Process,
            channel: ProcessOutputChannel,
            fd: Fd,
            *,
            event_callbacks: EventCallbacks,
            server_config: ServerConfig,
    ) -> None:
        super().__init__()

        self._process = process  # process which "owns" this dispatcher
        self._channel = channel  # 'stderr' or 'stdout'
        self._fd = fd
        self._event_callbacks = event_callbacks
        self._server_config = server_config

        self._closed = False  # True if close() has been called

    #

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} at {id(self)} for {self._process} ({self._channel})>'

    #

    @property
    def process(self) -> Process:
        return self._process

    @property
    def channel(self) -> ProcessOutputChannel:
        return self._channel

    def fd(self) -> Fd:
        return self._fd

    @property
    def closed(self) -> bool:
        return self._closed

    #

    def close(self) -> None:
        if not self._closed:
            log.debug('fd %s closed, stopped monitoring %s', self._fd, self)
            self._closed = True

    def on_error(self, exc: ta.Optional[BaseException] = None) -> None:
        nil, t, v, tbinfo = compact_traceback()

        log.critical('uncaptured python exception, closing channel %s (%s:%s %s)', repr(self), t, v, tbinfo)
        self.close()


class ProcessOutputDispatcherImpl(BaseProcessDispatcherImpl, ProcessOutputDispatcher):
    """
    Dispatcher for one channel (stdout or stderr) of one process. Serves several purposes:

    - capture output sent within <!--XSUPERVISOR:BEGIN--> and <!--XSUPERVISOR:END--> tags and signal a
      ProcessCommunicationEvent by calling notify_event(event).
    - route the output to the appropriate log handlers as specified in the config.
    """

    def __init__(
            self,
            process: Process,
            event_type: ta.Type[ProcessCommunicationEvent],
            fd: Fd,
            *,
            event_callbacks: EventCallbacks,
            server_config: ServerConfig,
    ) -> None:
        super().__init__(
            process,
            event_type.channel,
            fd,
            event_callbacks=event_callbacks,
            server_config=server_config,
        )

        self._event_type = event_type

        self._lc: ProcessConfig.Log = getattr(process.config, self._channel)

        self._init_normal_log()
        self._init_capture_log()

        self._child_log = self._normal_log

        self._capture_mode = False  # are we capturing process event data
        self._output_buffer = b''  # data waiting to be logged

        # all code below is purely for minor speedups

        begin_token = self._event_type.BEGIN_TOKEN
        end_token = self._event_type.END_TOKEN
        self._begin_token_data = (begin_token, len(begin_token))
        self._end_token_data = (end_token, len(end_token))

        self._main_log_level = logging.DEBUG

        self._log_to_main_log = self._server_config.loglevel <= self._main_log_level

        self._stdout_events_enabled = self._process.config.stdout.events_enabled
        self._stderr_events_enabled = self._process.config.stderr.events_enabled

    _child_log: ta.Optional[logging.Logger] = None  # the current logger (normal_log or capture_log)
    _normal_log: ta.Optional[logging.Logger] = None  # the "normal" (non-capture) logger
    _capture_log: ta.Optional[logging.Logger] = None  # the logger used while we're in capture_mode

    def _init_normal_log(self) -> None:
        """
        Configure the "normal" (non-capture) log for this channel of this process. Sets self.normal_log if logging is
        enabled.
        """

        config = self._process.config  # noqa
        channel = self._channel  # noqa

        logfile = self._lc.file
        max_bytes = self._lc.max_bytes  # noqa
        backups = self._lc.backups  # noqa
        to_syslog = self._lc.syslog

        if logfile or to_syslog:
            self._normal_log = logging.getLogger(__name__)

        # if logfile:
        #     loggers.handle_file(
        #         self.normal_log,
        #         filename=logfile,
        #         fmt='%(message)s',
        #         rotating=bool(max_bytes),  # optimization
        #         max_bytes=max_bytes,
        #         backups=backups,
        #     )

        # if to_syslog:
        #     loggers.handle_syslog(
        #         self.normal_log,
        #         fmt=config.name + ' %(message)s',
        #     )

    def _init_capture_log(self) -> None:
        """
        Configure the capture log for this process. This log is used to temporarily capture output when special output
        is detected. Sets self.capture_log if capturing is enabled.
        """

        capture_max_bytes = self._lc.capture_max_bytes
        if capture_max_bytes:
            self._capture_log = logging.getLogger(__name__)
            # loggers.handle_boundIO(
            #     self._capture_log,
            #     fmt='%(message)s',
            #     max_bytes=capture_max_bytes,
            # )

    def remove_logs(self) -> None:
        for l in (self._normal_log, self._capture_log):
            if l is not None:
                for handler in l.handlers:
                    handler.remove()  # type: ignore
                    handler.reopen()  # type: ignore

    def reopen_logs(self) -> None:
        for l in (self._normal_log, self._capture_log):
            if l is not None:
                for handler in l.handlers:
                    handler.reopen()  # type: ignore

    def _log(self, data: ta.Union[str, bytes, None]) -> None:
        if not data:
            return

        if self._server_config.strip_ansi:
            data = strip_escapes(as_bytes(data))

        if self._child_log:
            self._child_log.info(data)

        if self._log_to_main_log:
            if not isinstance(data, bytes):
                text = data
            else:
                try:
                    text = data.decode('utf-8')
                except UnicodeDecodeError:
                    text = f'Undecodable: {data!r}'
            log.log(self._main_log_level, '%r %s output:\n%s', self._process.config.name, self._channel, text)  # noqa

        if self._channel == 'stdout':
            if self._stdout_events_enabled:
                self._event_callbacks.notify(ProcessLogStdoutEvent(self._process, self._process.pid, data))

        elif self._stderr_events_enabled:
            self._event_callbacks.notify(ProcessLogStderrEvent(self._process, self._process.pid, data))

    def record_output(self) -> None:
        if self._capture_log is None:
            # shortcut trying to find capture data
            data = self._output_buffer
            self._output_buffer = b''
            self._log(data)
            return

        if self._capture_mode:
            token, token_len = self._end_token_data
        else:
            token, token_len = self._begin_token_data

        if len(self._output_buffer) <= token_len:
            return  # not enough data

        data = self._output_buffer
        self._output_buffer = b''

        try:
            before, after = data.split(token, 1)
        except ValueError:
            after = None
            index = find_prefix_at_end(data, token)
            if index:
                self._output_buffer = self._output_buffer + data[-index:]
                data = data[:-index]
            self._log(data)
        else:
            self._log(before)
            self.toggle_capture_mode()
            self._output_buffer = after  # type: ignore

        if after:
            self.record_output()

    def toggle_capture_mode(self) -> None:
        self._capture_mode = not self._capture_mode

        if self._capture_log is not None:
            if self._capture_mode:
                self._child_log = self._capture_log
            else:
                for handler in self._capture_log.handlers:
                    handler.flush()
                data = self._capture_log.getvalue()  # type: ignore
                channel = self._channel
                procname = self._process.config.name
                event = self._event_type(self._process, self._process.pid, data)
                self._event_callbacks.notify(event)

                log.debug('%r %s emitted a comm event', procname, channel)
                for handler in self._capture_log.handlers:
                    handler.remove()  # type: ignore
                    handler.reopen()  # type: ignore
                self._child_log = self._normal_log

    def writable(self) -> bool:
        return False

    def readable(self) -> bool:
        if self._closed:
            return False
        return True

    def on_readable(self) -> None:
        data = read_fd(self._fd)
        self._output_buffer += data
        self.record_output()
        if not data:
            # if we get no data back from the pipe, it means that the child process has ended. See
            # mail.python.org/pipermail/python-dev/2004-August/046850.html
            self.close()


class ProcessInputDispatcherImpl(BaseProcessDispatcherImpl, ProcessInputDispatcher):
    def __init__(
            self,
            process: Process,
            channel: ProcessOutputChannel,
            fd: Fd,
            *,
            event_callbacks: EventCallbacks,
            server_config: ServerConfig,
    ) -> None:
        super().__init__(
            process,
            channel,
            fd,
            event_callbacks=event_callbacks,
            server_config=server_config,
        )

        self._input_buffer = b''

    def write(self, chars: ta.Union[bytes, str]) -> None:
        self._input_buffer += as_bytes(chars)

    def writable(self) -> bool:
        if self._input_buffer and not self._closed:
            return True
        return False

    def flush(self) -> None:
        # other code depends on this raising EPIPE if the pipe is closed
        sent = os.write(self._fd, as_bytes(self._input_buffer))
        self._input_buffer = self._input_buffer[sent:]

    def on_writable(self) -> None:
        if self._input_buffer:
            try:
                self.flush()
            except OSError as why:
                if why.args[0] == errno.EPIPE:
                    self._input_buffer = b''
                    self.close()
                else:
                    raise
