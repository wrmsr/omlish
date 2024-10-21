# ruff: noqa: UP006
import typing as ta

from omlish.lite.check import check_not_none


ProcessState = int  # ta.TypeAlias
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


class ProcessStates:
    STOPPED = 0
    STARTING = 10
    RUNNING = 20
    BACKOFF = 30
    STOPPING = 40
    EXITED = 100
    FATAL = 200
    UNKNOWN = 1000


STOPPED_STATES = (
    ProcessStates.STOPPED,
    ProcessStates.EXITED,
    ProcessStates.FATAL,
    ProcessStates.UNKNOWN,
)

RUNNING_STATES = (
    ProcessStates.RUNNING,
    ProcessStates.BACKOFF,
    ProcessStates.STARTING,
)

SIGNALLABLE_STATES = (
    ProcessStates.RUNNING,
    ProcessStates.STARTING,
    ProcessStates.STOPPING,
)


_process_states_by_code = _names_by_code(ProcessStates)


def get_process_state_description(code: ProcessState) -> str:
    return check_not_none(_process_states_by_code.get(code))


##


class SupervisorStates:
    FATAL = 2
    RUNNING = 1
    RESTARTING = 0
    SHUTDOWN = -1


_supervisor_states_by_code = _names_by_code(SupervisorStates)


def get_supervisor_state_description(code: SupervisorState) -> str:
    return check_not_none(_supervisor_states_by_code.get(code))
