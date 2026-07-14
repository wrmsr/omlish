"""
Original author: Joshua Haberman
https://github.com/haberman/vtparse/blob/198ea4382f824dbb3f0e5b5553a9eb3290764694/vtparse_tables.rb

==

https://vt100.net/emu/dec_ansi_parser
https://github.com/haberman/vtparse
"""
import typing as ta


##


class StateTransition(ta.NamedTuple):
    to_state: str


TransitionMap: ta.TypeAlias = ta.Mapping[
    int | range | str,
    str | StateTransition | tuple[str | StateTransition, ...],
]


##


# Define the anywhere transitions
ANYWHERE_TRANSITIONS: TransitionMap = {
    0x18: ('execute', StateTransition('ground')),
    0x1a: ('execute', StateTransition('ground')),
    range(0x80, 0x90): ('execute', StateTransition('ground')),
    range(0x91, 0x98): ('execute', StateTransition('ground')),
    0x99: ('execute', StateTransition('ground')),
    0x9a: ('execute', StateTransition('ground')),
    0x9c: StateTransition('ground'),
    0x1b: StateTransition('escape'),
    0x98: StateTransition('sos_pm_apc_string'),
    0x9e: StateTransition('sos_pm_apc_string'),
    0x9f: StateTransition('sos_pm_apc_string'),
    0x90: StateTransition('dcs_entry'),
    0x9d: StateTransition('osc_string'),
    0x9b: StateTransition('csi_entry'),
}


# Global states dictionary
STATES: ta.Mapping[str, TransitionMap] = {
    # Define state transitions
    'ground': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x20, 0x80): 'print',
    },

    'escape': {
        'on_entry': 'clear',
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        0x7f: 'ignore',
        range(0x20, 0x30): ('collect', StateTransition('escape_intermediate')),
        range(0x30, 0x50): ('esc_dispatch', StateTransition('ground')),
        range(0x51, 0x58): ('esc_dispatch', StateTransition('ground')),
        0x59: ('esc_dispatch', StateTransition('ground')),
        0x5a: ('esc_dispatch', StateTransition('ground')),
        0x5c: ('esc_dispatch', StateTransition('ground')),
        range(0x60, 0x7f): ('esc_dispatch', StateTransition('ground')),
        0x5b: StateTransition('csi_entry'),
        0x5d: StateTransition('osc_string'),
        0x50: StateTransition('dcs_entry'),
        0x58: StateTransition('sos_pm_apc_string'),
        0x5e: StateTransition('sos_pm_apc_string'),
        0x5f: StateTransition('sos_pm_apc_string'),
    },

    'escape_intermediate': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x20, 0x30): 'collect',
        0x7f: 'ignore',
        range(0x30, 0x7f): ('esc_dispatch', StateTransition('ground')),
    },

    'csi_entry': {
        'on_entry': 'clear',
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        0x7f: 'ignore',
        range(0x20, 0x30): ('collect', StateTransition('csi_intermediate')),
        0x3a: StateTransition('csi_ignore'),
        range(0x30, 0x3a): ('param', StateTransition('csi_param')),
        0x3b: ('param', StateTransition('csi_param')),
        range(0x3c, 0x40): ('collect', StateTransition('csi_param')),
        range(0x40, 0x7f): ('csi_dispatch', StateTransition('ground')),
    },

    'csi_ignore': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x20, 0x40): 'ignore',
        0x7f: 'ignore',
        range(0x40, 0x7f): StateTransition('ground'),
    },

    'csi_param': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x30, 0x3a): 'param',
        0x3b: 'param',
        0x7f: 'ignore',
        0x3a: StateTransition('csi_ignore'),
        range(0x3c, 0x40): StateTransition('csi_ignore'),
        range(0x20, 0x30): ('collect', StateTransition('csi_intermediate')),
        range(0x40, 0x7f): ('csi_dispatch', StateTransition('ground')),
    },

    'csi_intermediate': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x20, 0x30): 'collect',
        0x7f: 'ignore',
        range(0x30, 0x40): StateTransition('csi_ignore'),
        range(0x40, 0x7f): ('csi_dispatch', StateTransition('ground')),
    },

    'dcs_entry': {
        'on_entry': 'clear',
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x20): 'ignore',
        0x7f: 'ignore',
        0x3a: StateTransition('dcs_ignore'),
        range(0x20, 0x30): ('collect', StateTransition('dcs_intermediate')),
        range(0x30, 0x3a): ('param', StateTransition('dcs_param')),
        0x3b: ('param', StateTransition('dcs_param')),
        range(0x3c, 0x40): ('collect', StateTransition('dcs_param')),
        range(0x40, 0x7f): (StateTransition('dcs_passthrough')),
    },

    'dcs_intermediate': {
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x20): 'ignore',
        range(0x20, 0x30): 'collect',
        0x7f: 'ignore',
        range(0x30, 0x40): StateTransition('dcs_ignore'),
        range(0x40, 0x7f): StateTransition('dcs_passthrough'),
    },

    'dcs_ignore': {
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x80): 'ignore',
    },

    'dcs_param': {
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x20): 'ignore',
        range(0x30, 0x3a): 'param',
        0x3b: 'param',
        0x7f: 'ignore',
        0x3a: StateTransition('dcs_ignore'),
        range(0x3c, 0x40): StateTransition('dcs_ignore'),
        range(0x20, 0x30): ('collect', StateTransition('dcs_intermediate')),
        range(0x40, 0x7f): StateTransition('dcs_passthrough'),
    },

    'dcs_passthrough': {
        'on_entry': 'hook',
        range(0x18): 'put',
        0x19: 'put',
        range(0x1c, 0x20): 'put',
        range(0x20, 0x7f): 'put',
        0x7f: 'ignore',
        'on_exit': 'unhook',
    },

    'sos_pm_apc_string': {
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x80): 'ignore',
    },

    'osc_string': {
        'on_entry': 'osc_start',
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x20): 'ignore',
        range(0x20, 0x80): 'osc_put',
        'on_exit': 'osc_end',
    },
}


##


ACTIONS_IN_ORDER = sorted(
    action
    for state, transitions in STATES.items()
    for keys, actions in transitions.items()
    for action in ([actions] if not isinstance(actions, tuple) else actions)
    if isinstance(action, str)
)

STATES_IN_ORDER = sorted(STATES)


##


TransitionTable: ta.TypeAlias = tuple[tuple[str | StateTransition, ...], ...]


def _build_state_tables() -> ta.Mapping[str, TransitionTable]:
    # Expand the range-based data structures into fully expanded tables
    state_tables: dict[str, list] = {}

    def expand_ranges(dct):
        array = [None] * 256
        for k, v in dct.items():
            if isinstance(k, range):
                for i in k:
                    array[i] = v
            elif isinstance(k, int):
                array[k] = v
        return array

    for s, t in STATES.items():
        state_tables[s] = expand_ranges(t)

    # Seed all the states with the anywhere transitions
    anywhere_transitions_expanded = expand_ranges(ANYWHERE_TRANSITIONS)

    for state, transitions in state_tables.items():
        for i, transition in enumerate(anywhere_transitions_expanded):
            if transition is not None:
                if transitions[i] is not None:
                    raise ValueError(
                        f'State {state} already had a transition defined for 0x{i:02x}, but that transition is also an '
                        f'anywhere transition!',
                    )
                transitions[i] = transition

    # For consistency, make all transitions tuples of actions
    return {
        state: tuple(tuple(t if isinstance(t, (list, tuple)) else [t]) for t in transitions)
        for state, transitions in state_tables.items()
    }


STATE_TABLES = _build_state_tables()


##


def check_state_tables(state_tables: ta.Mapping[str, TransitionTable]) -> None:
    for state, transitions in state_tables.items():
        for i, val in enumerate(transitions):
            if not val:
                raise ValueError(f'No transition defined from state {state}, char 0x{i:02x}!')
