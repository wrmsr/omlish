import enum
import signal
import typing as ta

from omlish import dataclasses as dc


Time: ta.TypeAlias = float


class LogConfig:
    logfile = logfiles['stdout_logfile']
    capture_maxbytes = stdout_cmaxbytes
    events_enabled = stdout_events
    logfile_backups = logfiles['stdout_logfile_backups']
    logfile_maxbytes = logfiles['stdout_logfile_maxbytes']
    syslog = logfiles['stdout_syslog']


class ProcessConfig:
    name: str
    command: ta.Sequence[str]
    directory: str | None = None
    umask: int | None = None
    uid: int | None = None
    priority: int = 999
    environment: ta.Mapping[str, str] | None = None

    serverurl: str = None

    autostart: bool = True
    autorestart: str = 'unexpected'
    startsecs: float = 1.
    startretries: int = 3

    stopsignal: int = signal.SIGTERM
    stopwaitsecs: float = 10.
    stopasgroup: bool = False
    killasgroup: bool = dc.field(derive=lambda stopasgroup: stopasgroup)
    exitcodes: ta.Sequence[int] = (0,)

    redirect_stderr: bool = False

    stdout: LogConfig = LogConfig()
    stderr: LogConfig = LogConfig()


class ProcessState(enum.Enum):
    STOPPED = enum.auto()
    STARTING = enum.auto()
    RUNNING = enum.auto()
    BACKOFF = enum.auto()
    STOPPING = enum.auto()
    EXITED = enum.auto()
    FATAL = enum.auto()
    UNKNOWN = enum.auto()


STOPPED_STATES = frozenset([
    ProcessState.STOPPED,
    ProcessState.EXITED,
    ProcessState.FATAL,
    ProcessState.UNKNOWN,
])

RUNNING_STATES = frozenset([
    ProcessState.RUNNING,
    ProcessState.BACKOFF,
    ProcessState.STARTING,
])

SIGNALLABLE_STATES = frozenset([
    ProcessState.RUNNING,
    ProcessState.STARTING,
    ProcessState.STOPPING,
])


class SupervisorStates(enum.Enum):
    FATAL = enum.auto()
    RUNNING = enum.auto()
    RESTARTING = enum.auto()
    SHUTDOWN = enum.auto()


class EventListenerStates(enum.Enum):
    READY = enum.auto()  # the process ready to be sent an event from supervisor
    BUSY = enum.auto()  # event listener is processing an event sent to it by supervisor
    ACKNOWLEDGED = enum.auto()  # the event listener processed an event
    UNKNOWN = enum.auto()  # the event listener is in an unknown state


class Process:

    pid: int = 0  # Subprocess pid; 0 when not running
    config: ProcessConfig
    state: ProcessState | None = None  # process state code
    listener_state = None  # listener state code (if we're an event listener)
    event = None  # event currently being processed (if we're an event listener)
    laststart: Time | None = None  # Last time the subprocess was started
    laststop: Time | None = None  # Last time the subprocess was stopped
    laststopreport: Time | None = None  # Last time "waiting for x to stop" logged, to throttle
    delay: float | None = None  # If present, delay starting or killing until this time
    administrative_stop = False  # true if process has been stopped by an admin
    system_stop = False  # true if process has been stopped by the system
    killing: bool = False  # true if we are trying to kill this process
    backoff: int = 0  # backoff counter (to startretries)
    dispatchers = None  # asyncore output dispatchers (keyed by fd)
    pipes: ta.Mapping[str, int] | None = None  # map of channel name to file descriptor #
    exitstatus: int | None = None  # status attached to dead process by finish()
    spawnerr = None  # error message attached by spawn() if any
    group: ProcessGroup | None = None  # ProcessGroup instance if process is in the group

