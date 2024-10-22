# ruff: noqa: UP007
import abc
import errno
import logging
import os
import typing as ta

from .compat import as_bytes
from .compat import compact_traceback
from .compat import find_prefix_at_end
from .compat import readfd
from .compat import strip_escapes
from .configs import ProcessConfig
from .events import ProcessLogStderrEvent
from .events import ProcessLogStdoutEvent
from .events import notify_event
from .types import AbstractSubprocess


log = logging.getLogger(__name__)


class Dispatcher(abc.ABC):

    def __init__(self, process: AbstractSubprocess, channel: str, fd: int) -> None:
        super().__init__()

        self._process = process  # process which "owns" this dispatcher
        self._channel = channel  # 'stderr' or 'stdout'
        self._fd = fd
        self._closed = False  # True if close() has been called

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} at {id(self)} for {self._process} ({self._channel})>'

    @property
    def process(self) -> AbstractSubprocess:
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

    @abc.abstractmethod
    def readable(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def writable(self) -> bool:
        raise NotImplementedError

    def handle_read_event(self) -> None:
        raise TypeError

    def handle_write_event(self) -> None:
        raise TypeError

    def handle_error(self) -> None:
        nil, t, v, tbinfo = compact_traceback()

        log.critical('uncaptured python exception, closing channel %s (%s:%s %s)', repr(self), t, v, tbinfo)
        self.close()

    def close(self) -> None:
        if not self._closed:
            log.debug('fd %s closed, stopped monitoring %s', self._fd, self)
            self._closed = True

    def flush(self) -> None:  # noqa
        pass


class OutputDispatcher(Dispatcher):
    """
    Dispatcher for one channel (stdout or stderr) of one process. Serves several purposes:

    - capture output sent within <!--XSUPERVISOR:BEGIN--> and <!--XSUPERVISOR:END--> tags and signal a
      ProcessCommunicationEvent by calling notify_event(event).
    - route the output to the appropriate log handlers as specified in the config.
    """

    def __init__(self, process: AbstractSubprocess, event_type, fd):
        """
        Initialize the dispatcher.

        `event_type` should be one of ProcessLogStdoutEvent or ProcessLogStderrEvent
        """
        super().__init__(process, event_type.channel, fd)
        self.event_type = event_type

        self.lc: ProcessConfig.Log = getattr(process.config, self._channel)

        self._init_normal_log()
        self._init_capture_log()

        self._child_log = self._normal_log

        self._capture_mode = False  # are we capturing process event data
        self._output_buffer = b''  # data waiting to be logged

        # all code below is purely for minor speedups
        begin_token = self.event_type.BEGIN_TOKEN
        end_token = self.event_type.END_TOKEN
        self.begin_token_data = (begin_token, len(begin_token))
        self.end_token_data = (end_token, len(end_token))
        self.main_log_level = logging.DEBUG
        config = self._process.config
        self.log_to_main_log = process.context.config.loglevel <= self.main_log_level
        self.stdout_events_enabled = config.stdout.events_enabled
        self.stderr_events_enabled = config.stderr.events_enabled

    _child_log: ta.Optional[logging.Logger]  # the current logger (normal_log or capture_log)
    _normal_log: ta.Optional[logging.Logger]  # the "normal" (non-capture) logger
    _capture_log: ta.Optional[logging.Logger]  # the logger used while we're in capture_mode

    def _init_normal_log(self) -> None:
        """
        Configure the "normal" (non-capture) log for this channel of this process. Sets self.normal_log if logging is
        enabled.
        """
        config = self._process.config  # noqa
        channel = self._channel  # noqa

        logfile = self.lc.file
        maxbytes = self.lc.maxbytes  # noqa
        backups = self.lc.backups  # noqa
        to_syslog = self.lc.syslog

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
        #
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
        capture_maxbytes = self.lc.capture_maxbytes
        if capture_maxbytes:
            self._capture_log = logging.getLogger(__name__)
            # loggers.handle_boundIO(
            #     self._capture_log,
            #     fmt='%(message)s',
            #     maxbytes=capture_maxbytes,
            # )

    def remove_logs(self):
        for log in (self._normal_log, self._capture_log):
            if log is not None:
                for handler in log.handlers:
                    handler.remove()  # type: ignore
                    handler.reopen()  # type: ignore

    def reopen_logs(self):
        for log in (self._normal_log, self._capture_log):
            if log is not None:
                for handler in log.handlers:
                    handler.reopen()  # type: ignore

    def _log(self, data):
        if data:
            if self._process.context.config.strip_ansi:
                data = strip_escapes(data)
            if self._child_log:
                self._child_log.info(data)
            if self.log_to_main_log:
                if not isinstance(data, bytes):
                    text = data
                else:
                    try:
                        text = data.decode('utf-8')
                    except UnicodeDecodeError:
                        text = f'Undecodable: {data!r}'
                log.log(self.main_log_level, '%r %s output:\n%s', self._process.config.name, self._channel, text)  # noqa
            if self._channel == 'stdout':
                if self.stdout_events_enabled:
                    notify_event(ProcessLogStdoutEvent(self._process, self._process.pid, data))
            elif self.stderr_events_enabled:
                notify_event(ProcessLogStderrEvent(self._process, self._process.pid, data))

    def record_output(self):
        if self._capture_log is None:
            # shortcut trying to find capture data
            data = self._output_buffer
            self._output_buffer = b''
            self._log(data)
            return

        if self._capture_mode:
            token, tokenlen = self.end_token_data
        else:
            token, tokenlen = self.begin_token_data

        if len(self._output_buffer) <= tokenlen:
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

    def toggle_capture_mode(self):
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
                event = self.event_type(self._process, self._process.pid, data)
                notify_event(event)

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
        data = readfd(self._fd)
        self._output_buffer += data
        self.record_output()
        if not data:
            # if we get no data back from the pipe, it means that the child process has ended.  See
            # mail.python.org/pipermail/python-dev/2004-August/046850.html
            self.close()


class InputDispatcher(Dispatcher):

    def __init__(self, process: AbstractSubprocess, channel: str, fd: int) -> None:
        super().__init__(process, channel, fd)
        self._input_buffer = b''

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
