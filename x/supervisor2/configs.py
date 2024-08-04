import os

from .compat import get_path
from .datatypes import Automatic


class Config:
    priority: int
    name: str

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.name < other.name
        return self.priority < other.priority

    def __le__(self, other):
        if self.priority == other.priority:
            return self.name <= other.name
        return self.priority <= other.priority

    def __gt__(self, other):
        if self.priority == other.priority:
            return self.name > other.name
        return self.priority > other.priority

    def __ge__(self, other):
        if self.priority == other.priority:
            return self.name >= other.name
        return self.priority >= other.priority

    def __repr__(self):
        return '<%s instance at %s named %s>' % (self.__class__, id(self), self.name)


class ProcessConfig(Config):
    req_param_names = [
        'name',

        'uid',
        'command',
        'directory',
        'umask',
        'priority',

        'autostart',
        'autorestart',

        'startsecs',
        'startretries',

        'stdout_logfile',
        'stdout_capture_maxbytes',
        'stdout_events_enabled',
        'stdout_syslog',
        'stdout_logfile_backups',
        'stdout_logfile_maxbytes',

        'stderr_logfile',
        'stderr_capture_maxbytes',
        'stderr_logfile_backups',
        'stderr_logfile_maxbytes',
        'stderr_events_enabled',
        'stderr_syslog',

        'stopsignal',
        'stopwaitsecs',
        'stopasgroup',

        'killasgroup',

        'exitcodes',

        'redirect_stderr',
    ]

    optional_param_names = [
        'environment',
    ]

    def __init__(self, options, **params):
        self.options = options
        for name in self.req_param_names:
            setattr(self, name, params[name])
        for name in self.optional_param_names:
            setattr(self, name, params.get(name, None))

    def __eq__(self, other):
        if not isinstance(other, ProcessConfig):
            return False

        for name in self.req_param_names + self.optional_param_names:
            if Automatic in [getattr(self, name), getattr(other, name)]:
                continue
            if getattr(self, name) != getattr(other, name):
                return False

        return True

    def get_path(self):
        """
        Return a list corresponding to $PATH that is configured to be set in the process environment, or the system
        default.
        """
        if self.environment is not None:
            path = self.environment.get('PATH')
            if path is not None:
                return path.split(os.pathsep)
        return get_path()

    def create_auto_child_logs(self):
        # temporary logfiles which are erased at start time
        get_autoname = self.options.get_auto_child_log_name
        sid = self.options.identifier
        name = self.name
        if self.stdout_logfile is Automatic:
            self.stdout_logfile = get_autoname(name, sid, 'stdout')
        if self.stderr_logfile is Automatic:
            self.stderr_logfile = get_autoname(name, sid, 'stderr')

    def make_process(self, group=None):
        from .process import Subprocess
        process = Subprocess(self)
        process.group = group
        return process

    def make_dispatchers(self, proc):
        use_stderr = not self.redirect_stderr
        from .options import make_pipes
        p = make_pipes(use_stderr)
        stdout_fd, stderr_fd, stdin_fd = p['stdout'], p['stderr'], p['stdin']
        dispatchers = {}
        from . import events
        from .dispatchers import PInputDispatcher
        from .dispatchers import POutputDispatcher
        if stdout_fd is not None:
            etype = events.ProcessCommunicationStdoutEvent
            dispatchers[stdout_fd] = POutputDispatcher(proc, etype, stdout_fd)
        if stderr_fd is not None:
            etype = events.ProcessCommunicationStderrEvent
            dispatchers[stderr_fd] = POutputDispatcher(proc, etype, stderr_fd)
        if stdin_fd is not None:
            dispatchers[stdin_fd] = PInputDispatcher(proc, 'stdin', stdin_fd)
        return dispatchers, p


class EventListenerConfig(ProcessConfig):
    def make_dispatchers(self, proc):
        # always use_stderr=True for eventlisteners because mixing stderr messages into stdout would break the
        # eventlistener protocol
        use_stderr = True
        from .options import make_pipes
        p = make_pipes(use_stderr)
        stdout_fd, stderr_fd, stdin_fd = p['stdout'], p['stderr'], p['stdin']
        dispatchers = {}
        from . import events
        from .dispatchers import PEventListenerDispatcher
        from .dispatchers import PInputDispatcher
        from .dispatchers import POutputDispatcher
        if stdout_fd is not None:
            dispatchers[stdout_fd] = PEventListenerDispatcher(proc, 'stdout', stdout_fd)
        if stderr_fd is not None:
            etype = events.ProcessCommunicationStderrEvent
            dispatchers[stderr_fd] = POutputDispatcher(proc, etype, stderr_fd)
        if stdin_fd is not None:
            dispatchers[stdin_fd] = PInputDispatcher(proc, 'stdin', stdin_fd)
        return dispatchers, p


class ProcessGroupConfig(Config):
    def __init__(self, options, name, priority, process_configs):
        self.options = options
        self.name = name
        self.priority = priority
        self.process_configs = process_configs

    def __eq__(self, other):
        if not isinstance(other, ProcessGroupConfig):
            return False

        if self.name != other.name:
            return False
        if self.priority != other.priority:
            return False
        if self.process_configs != other.process_configs:
            return False

        return True

    def after_setuid(self):
        for config in self.process_configs:
            config.create_auto_child_logs()

    def make_group(self):
        from .process import ProcessGroup
        return ProcessGroup(self)


class EventListenerPoolConfig(Config):
    def __init__(
            self,
            options,
            name,
            priority,
            process_configs,
            buffer_size,
            pool_events,
            result_handler,
    ):
        self.options = options
        self.name = name
        self.priority = priority
        self.process_configs = process_configs
        self.buffer_size = buffer_size
        self.pool_events = pool_events
        self.result_handler = result_handler

    def __eq__(self, other):
        if not isinstance(other, EventListenerPoolConfig):
            return False

        if (
                self.name == other.name and
                self.priority == other.priority and
                self.process_configs == other.process_configs and
                self.buffer_size == other.buffer_size and
                self.pool_events == other.pool_events and
                self.result_handler == other.result_handler
        ):
            return True

        return False

    def after_setuid(self):
        for config in self.process_configs:
            config.create_auto_child_logs()

    def make_group(self):
        from .process import EventListenerPool
        return EventListenerPool(self)
