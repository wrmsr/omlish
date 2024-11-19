# ruff: noqa: UP006
import enum
import typing as ta

from omlish.lite.check import check_not_none


SupervisorState = int  # ta.TypeAlias


##


def _names_by_code(states: ta.Any) -> ta.Dict[int, str]:
    d = {}
    for name in states.__dict__:
        if not name.startswith('__'):
            code = getattr(states, name)
            d[code] = name
    return d


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


def get_process_state_description(code: ProcessState) -> str:
    return code.name


##


class SupervisorStates:
    FATAL = 2
    RUNNING = 1
    RESTARTING = 0
    SHUTDOWN = -1


_supervisor_states_by_code = _names_by_code(SupervisorStates)


def get_supervisor_state_description(code: SupervisorState) -> str:
    return check_not_none(_supervisor_states_by_code.get(code))
