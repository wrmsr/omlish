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


if ta.TYPE_CHECKING:
    from .process import Subprocess


log = logging.getLogger(__name__)


class Dispatcher:

    def __init__(self, process: 'Subprocess', channel: str, fd: int) -> None:
        super().__init__()

        self.process = process  # process which "owns" this dispatcher
        self.channel = channel  # 'stderr' or 'stdout'
        self.fd = fd
        self.closed = False  # True if close() has been called

    def __repr__(self) -> str:
        return '<%s at %s for %s (%s)>' % (self.__class__.__name__, id(self), self.process, self.channel)

    def readable(self):
        raise NotImplementedError

    def writable(self):
        raise NotImplementedError

    def handle_read_event(self):
        raise NotImplementedError

    def handle_write_event(self):
        raise NotImplementedError

    def handle_error(self):
        nil, t, v, tbinfo = compact_traceback()

        log.critical(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (repr(self), t, v, tbinfo),
        )
        self.close()

    def close(self):
        if not self.closed:
            log.debug('fd %s closed, stopped monitoring %s' % (self.fd, self))
            self.closed = True

    def flush(self):
        pass


class OutputDispatcher(Dispatcher):
    """
    Dispatcher for one channel (stdout or stderr) of one process. Serves several purposes:

    - capture output sent within <!--XSUPERVISOR:BEGIN--> and <!--XSUPERVISOR:END--> tags and signal a
      ProcessCommunicationEvent by calling notify_event(event).
    - route the output to the appropriate log handlers as specified in the config.
    """

    child_log = None  # the current logger (normal_log or capture_log)
    normal_log = None  # the "normal" (non-capture) logger
    capture_log = None  # the logger used while we're in capture_mode
    capture_mode = False  # are we capturing process event data
    output_buffer = b''  # data waiting to be logged

    def __init__(self, process: 'Subprocess', event_type, fd):
        """
        Initialize the dispatcher.

        `event_type` should be one of ProcessLogStdoutEvent or ProcessLogStderrEvent
        """
        super().__init__(process, event_type.channel, fd)
        self.event_type = event_type

        self.lc: ProcessConfig.Log = getattr(process.config, self.channel)

        self._init_normal_log()
        self._init_capture_log()

        self.child_log = self.normal_log

        # all code below is purely for minor speedups
        begin_token = self.event_type.BEGIN_TOKEN
        end_token = self.event_type.END_TOKEN
        self.begin_token_data = (begin_token, len(begin_token))
        self.end_token_data = (end_token, len(end_token))
        self.main_log_level = logging.DEBUG
        config = self.process.config
        self.log_to_main_log = process.context.config.loglevel <= self.main_log_level
        self.stdout_events_enabled = config.stdout.events_enabled
        self.stderr_events_enabled = config.stderr.events_enabled

    def _init_normal_log(self):
        """
        Configure the "normal" (non-capture) log for this channel of this process. Sets self.normal_log if logging is
        enabled.
        """
        config = self.process.config
        channel = self.channel

        logfile = self.lc.file
        maxbytes = self.lc.maxbytes
        backups = self.lc.backups
        to_syslog = self.lc.syslog

        if logfile or to_syslog:
            self.normal_log = logging.getLogger(__name__)

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

    def _init_capture_log(self):
        """
        Configure the capture log for this process.  This log is used to temporarily capture output when special output
        is detected. Sets self.capture_log if capturing is enabled.
        """
        capture_maxbytes = self.lc.capture_maxbytes
        if capture_maxbytes:
            self.capture_log = logging.getLogger(__name__)
            # loggers.handle_boundIO(
            #     self.capture_log,
            #     fmt='%(message)s',
            #     maxbytes=capture_maxbytes,
            # )

    def remove_logs(self):
        for log in (self.normal_log, self.capture_log):
            if log is not None:
                for handler in log.handlers:
                    handler.remove()
                    handler.reopen()

    def reopen_logs(self):
        for log in (self.normal_log, self.capture_log):
            if log is not None:
                for handler in log.handlers:
                    handler.reopen()

    def _log(self, data):
        if data:
            if self.process.context.config.strip_ansi:
                data = strip_escapes(data)
            if self.child_log:
                self.child_log.info(data)
            if self.log_to_main_log:
                if not isinstance(data, bytes):
                    text = data
                else:
                    try:
                        text = data.decode('utf-8')
                    except UnicodeDecodeError:
                        text = 'Undecodable: %r' % data
                msg = '%(name)r %(channel)s output:\n%(data)s'
                log.log(
                    self.main_log_level, msg, name=self.process.config.name,
                    channel=self.channel, data=text)
            if self.channel == 'stdout':
                if self.stdout_events_enabled:
                    notify_event(ProcessLogStdoutEvent(self.process, self.process.pid, data))
            elif self.stderr_events_enabled:
                notify_event(ProcessLogStderrEvent(self.process, self.process.pid, data))

    def record_output(self):
        if self.capture_log is None:
            # shortcut trying to find capture data
            data = self.output_buffer
            self.output_buffer = b''
            self._log(data)
            return

        if self.capture_mode:
            token, tokenlen = self.end_token_data
        else:
            token, tokenlen = self.begin_token_data

        if len(self.output_buffer) <= tokenlen:
            return  # not enough data

        data = self.output_buffer
        self.output_buffer = b''

        try:
            before, after = data.split(token, 1)
        except ValueError:
            after = None
            index = find_prefix_at_end(data, token)
            if index:
                self.output_buffer = self.output_buffer + data[-index:]
                data = data[:-index]
            self._log(data)
        else:
            self._log(before)
            self.toggle_capture_mode()
            self.output_buffer = after

        if after:
            self.record_output()

    def toggle_capture_mode(self):
        self.capture_mode = not self.capture_mode

        if self.capture_log is not None:
            if self.capture_mode:
                self.child_log = self.capture_log
            else:
                for handler in self.capture_log.handlers:
                    handler.flush()
                data = self.capture_log.getvalue()
                channel = self.channel
                procname = self.process.config.name
                event = self.event_type(self.process, self.process.pid, data)
                notify_event(event)

                msg = '%(procname)r %(channel)s emitted a comm event'
                log.debug(msg, procname=procname, channel=channel)
                for handler in self.capture_log.handlers:
                    handler.remove()
                    handler.reopen()
                self.child_log = self.normal_log

    def writable(self):
        return False

    def readable(self):
        if self.closed:
            return False
        return True

    def handle_read_event(self):
        data = readfd(self.fd)
        self.output_buffer += data
        self.record_output()
        if not data:
            # if we get no data back from the pipe, it means that the child process has ended.  See
            # mail.python.org/pipermail/python-dev/2004-August/046850.html
            self.close()


class InputDispatcher(Dispatcher):

    def __init__(self, process, channel, fd):
        super().__init__(process, channel, fd)
        self.input_buffer = b''

    def writable(self):
        if self.input_buffer and not self.closed:
            return True
        return False

    def readable(self):
        return False

    def flush(self):
        # other code depends on this raising EPIPE if the pipe is closed
        sent = os.write(self.fd, as_bytes(self.input_buffer))
        self.input_buffer = self.input_buffer[sent:]

    def handle_write_event(self):
        if self.input_buffer:
            try:
                self.flush()
            except OSError as why:
                if why.args[0] == errno.EPIPE:
                    self.input_buffer = b''
                    self.close()
                else:
                    raise
