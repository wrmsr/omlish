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

    @property
    def stopped(self) -> bool:
        return self in STOPPED_STATES

    @property
    def running(self) -> bool:
        return self in RUNNING_STATES

    @property
    def signalable(self) -> bool:
        return self in SIGNALABLE_STATES


# http://supervisord.org/subprocess.html
STATE_TRANSITIONS = {
    ProcessState.STOPPED: (ProcessState.STARTING,),
    ProcessState.STARTING: (ProcessState.RUNNING, ProcessState.BACKOFF, ProcessState.STOPPING),
    ProcessState.RUNNING: (ProcessState.STOPPING, ProcessState.EXITED),
    ProcessState.BACKOFF: (ProcessState.STARTING, ProcessState.FATAL),
    ProcessState.STOPPING: (ProcessState.STOPPED,),
    ProcessState.EXITED: (ProcessState.STARTING,),
    ProcessState.FATAL: (ProcessState.STARTING,),
}

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
