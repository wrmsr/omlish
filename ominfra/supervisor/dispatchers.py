# ruff: noqa: UP006 UP007
import abc
import errno
import logging
import os
import typing as ta

from omlish.lite.logs import log

from .configs import ProcessConfig
from .events import EventCallbacks
from .events import ProcessCommunicationEvent
from .events import ProcessLogStderrEvent
from .events import ProcessLogStdoutEvent
from .types import Dispatcher
from .types import InputDispatcher
from .types import OutputDispatcher
from .types import Process
from .utils import as_bytes
from .utils import compact_traceback
from .utils import find_prefix_at_end
from .utils import read_fd
from .utils import strip_escapes


##


class BaseDispatcherImpl(Dispatcher, abc.ABC):
    def __init__(
            self,
            process: Process,
            channel: str,
            fd: int,
            *,
            event_callbacks: EventCallbacks,
    ) -> None:
        super().__init__()

        self._process = process  # process which "owns" this dispatcher
        self._channel = channel  # 'stderr' or 'stdout'
        self._fd = fd
        self._event_callbacks = event_callbacks

        self._closed = False  # True if close() has been called

    #

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} at {id(self)} for {self._process} ({self._channel})>'

    #

    @property
    def process(self) -> Process:
        return self._process

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def fd(self) -> int:
        return self._fd

    @property
    def closed(self) -> bool:
        return self._closed

    #

    def close(self) -> None:
        if not self._closed:
            log.debug('fd %s closed, stopped monitoring %s', self._fd, self)
            self._closed = True

    def handle_error(self) -> None:
        nil, t, v, tbinfo = compact_traceback()

        log.critical('uncaptured python exception, closing channel %s (%s:%s %s)', repr(self), t, v, tbinfo)
        self.close()


class OutputDispatcherImpl(BaseDispatcherImpl, OutputDispatcher):
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
            fd: int,
            *,
            event_callbacks: EventCallbacks,
    ) -> None:
        super().__init__(
            process,
            event_type.channel,
            fd,
            event_callbacks=event_callbacks,
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

        self._log_to_main_log = process.context.config.loglevel <= self._main_log_level

        config = self._process.config
        self._stdout_events_enabled = config.stdout.events_enabled
        self._stderr_events_enabled = config.stderr.events_enabled

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
        maxbytes = self._lc.maxbytes  # noqa
        backups = self._lc.backups  # noqa
        to_syslog = self._lc.syslog

        if logfile or to_syslog:
            self._normal_log = logging.getLogger(__name__)

        # if logfile:
        #     loggers.handle_file(
        #         self.normal_log,
        #         filename=logfile,
        #         fmt='%(message)s',
        #         rotating=bool(maxbytes),  # optimization
        #         maxbytes=maxbytes,
        #         backups=backups,
        #     )

        # if to_syslog:
        #     loggers.handle_syslog(
        #         self.normal_log,
        #         fmt=config.name + ' %(message)s',
        #     )

    def _init_capture_log(self) -> None:
        """
        Configure the capture log for this process.  This log is used to temporarily capture output when special output
        is detected. Sets self.capture_log if capturing is enabled.
        """

        capture_maxbytes = self._lc.capture_maxbytes
        if capture_maxbytes:
            self._capture_log = logging.getLogger(__name__)
            # loggers.handle_boundIO(
            #     self._capture_log,
            #     fmt='%(message)s',
            #     maxbytes=capture_maxbytes,
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

        if self._process.context.config.strip_ansi:
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

    def handle_read_event(self) -> None:
        data = read_fd(self._fd)
        self._output_buffer += data
        self.record_output()
        if not data:
            # if we get no data back from the pipe, it means that the child process has ended.  See
            # mail.python.org/pipermail/python-dev/2004-August/046850.html
            self.close()


class InputDispatcherImpl(BaseDispatcherImpl, InputDispatcher):
    def __init__(
            self,
            process: Process,
            channel: str,
            fd: int,
            *,
            event_callbacks: EventCallbacks,
    ) -> None:
        super().__init__(
            process,
            channel,
            fd,
            event_callbacks=event_callbacks,
        )

        self._input_buffer = b''

    def write(self, chars: ta.Union[bytes, str]) -> None:
        self._input_buffer += as_bytes(chars)

    def writable(self) -> bool:
        if self._input_buffer and not self._closed:
            return True
        return False

    def readable(self) -> bool:
        return False

    def flush(self) -> None:
        # other code depends on this raising EPIPE if the pipe is closed
        sent = os.write(self._fd, as_bytes(self._input_buffer))
        self._input_buffer = self._input_buffer[sent:]

    def handle_write_event(self) -> None:
        if self._input_buffer:
            try:
                self.flush()
            except OSError as why:
                if why.args[0] == errno.EPIPE:
                    self._input_buffer = b''
                    self.close()
                else:
                    raise


##


class Dispatchers:
    def __init__(self, dispatchers: ta.Iterable[Dispatcher]) -> None:
        super().__init__()

        by_fd: ta.Dict[int, Dispatcher] = {}
        for d in dispatchers:
            if d.fd in by_fd:
                raise KeyError(f'fd {d.fd} of dispatcher {d} already registered by {by_fd[d.fd]}')
            by_fd[d.fd] = d
        self._by_fd = by_fd

    #

    def __iter__(self) -> ta.Iterator[Dispatcher]:
        return iter(self._by_fd.values())

    def __len__(self) -> int:
        return len(self._by_fd)

    def __contains__(self, fd: int) -> bool:
        return fd in self._by_fd

    def __getitem__(self, fd: int) -> Dispatcher:
        return self._by_fd[fd]

    def get(self, fd: int, default: ta.Optional[Dispatcher] = None) -> ta.Optional[Dispatcher]:
        return self._by_fd.get(fd, default)

    #

    def drain(self) -> None:
        for dispatcher in self:
            # note that we *must* call readable() for every dispatcher, as it may have side effects for a given
            # dispatcher (eg. call handle_listener_state_change for event listener processes)
            if dispatcher.readable():
                dispatcher.handle_read_event()
            if dispatcher.writable():
                dispatcher.handle_write_event()

    #

    def remove_logs(self) -> None:
        for dispatcher in self:
            if hasattr(dispatcher, 'remove_logs'):
                dispatcher.remove_logs()

    def reopen_logs(self) -> None:
        for dispatcher in self:
            if hasattr(dispatcher, 'reopen_logs'):
                dispatcher.reopen_logs()
