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


def get_process_state_description(code):
    return _process_states_by_code.get(code)


class SupervisorStates:
    FATAL = 2
    RUNNING = 1
    RESTARTING = 0
    SHUTDOWN = -1


def get_supervisor_state_description(code):
    return _supervisor_states_by_code.get(code)


class EventListenerStates:
    READY = 10  # the process ready to be sent an event from supervisor
    BUSY = 20  # event listener is processing an event sent to it by supervisor
    ACKNOWLEDGED = 30  # the event listener processed an event
    UNKNOWN = 40  # the event listener is in an unknown state


def get_event_listener_state_description(code):
    return _event_listener_states_by_code.get(code)


# below is an optimization for internal use in this module only
def _names_by_code(states):
    d = {}
    for name in states.__dict__:
        if not name.startswith('__'):
            code = getattr(states, name)
            d[code] = name
    return d


_process_states_by_code = _names_by_code(ProcessStates)
_supervisor_states_by_code = _names_by_code(SupervisorStates)
_event_listener_states_by_code = _names_by_code(EventListenerStates)
