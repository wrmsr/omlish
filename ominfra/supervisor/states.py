import enum


##


class ProcessState(enum.IntEnum):
    STOPPED = 0
    STARTING = 10
    RUNNING = 20
    BACKOFF = 30
    STOPPING = 40
    EXITED = 100
    FATAL = 200
    UNKNOWN = 1000


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

SIGNALLABLE_STATES = (
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
