import enum


##


class ProcessState(enum.IntEnum):
    """
    http://supervisord.org/subprocess.html

    STOPPED -> STARTING
    STARTING -> RUNNING, BACKOFF, STOPPING
    RUNNING -> STOPPING, EXITED
    BACKOFF -> STARTING, FATAL
    STOPPING -> STOPPED
    EXITED -> STARTING
    FATAL -> STARTING
    """

    STOPPED = 0
    STARTING = 10
    RUNNING = 20
    BACKOFF = 30
    STOPPING = 40
    EXITED = 100
    FATAL = 200
    UNKNOWN = 1000

    @property
    def stopped(self) -> bool:
        return self in STOPPED_STATES

    @property
    def running(self) -> bool:
        return self in RUNNING_STATES

    @property
    def signalable(self) -> bool:
        return self in SIGNALABLE_STATES


STOPPED_STATES = (
    ProcessState.STOPPED,
    ProcessState.EXITED,
    ProcessState.FATAL,
    ProcessState.UNKNOWN,
)

RUNNING_STATES = (
    ProcessState.RUNNING,
    ProcessState.BACKOFF,
    ProcessState.STARTING,
)

SIGNALABLE_STATES = (
    ProcessState.RUNNING,
    ProcessState.STARTING,
    ProcessState.STOPPING,
)


##


class SupervisorState(enum.IntEnum):
    FATAL = 2
    RUNNING = 1
    RESTARTING = 0
    SHUTDOWN = -1
