"""
https://vt100.net/emu/dec_ansi_parser

https://github.com/haberman/vtparse

==

https://github.com/alacritty/vte/blob/master/src/ansi.rs
https://crates.io/crates/vt100
"""
import typing as ta


##
# Original author: Joshua Haberman
# https://github.com/haberman/vtparse/blob/198ea4382f824dbb3f0e5b5553a9eb3290764694/vtparse_tables.rb


class StateTransition(ta.NamedTuple):
    to_state: str


TransitionTableEntry: ta.TypeAlias = str | StateTransition | tuple[str | StateTransition, ...]
TransitionTable: ta.TypeAlias = ta.Mapping[int | range | str, TransitionTableEntry]


# Define the anywhere transitions
ANYWHERE_TRANSITIONS: TransitionTable = {
    0x18: ('execute', StateTransition('GROUND')),
    0x1a: ('execute', StateTransition('GROUND')),
    range(0x80, 0x90): ('execute', StateTransition('GROUND')),
    range(0x91, 0x98): ('execute', StateTransition('GROUND')),
    0x99: ('execute', StateTransition('GROUND')),
    0x9a: ('execute', StateTransition('GROUND')),
    0x9c: StateTransition('GROUND'),
    0x1b: StateTransition('ESCAPE'),
    0x98: StateTransition('SOS_PM_APC_STRING'),
    0x9e: StateTransition('SOS_PM_APC_STRING'),
    0x9f: StateTransition('SOS_PM_APC_STRING'),
    0x90: StateTransition('DCS_ENTRY'),
    0x9d: StateTransition('OSC_STRING'),
    0x9b: StateTransition('CSI_ENTRY'),
}


# Global states dictionary
STATES: ta.Mapping[str, TransitionTable] = {
    # Define state transitions
    'GROUND': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x20, 0x80): 'print',
    },

    'ESCAPE': {
        'on_entry': 'clear',
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        0x7f: 'ignore',
        range(0x20, 0x30): ('collect', StateTransition('ESCAPE_INTERMEDIATE')),
        range(0x30, 0x50): ('esc_dispatch', StateTransition('GROUND')),
        range(0x51, 0x58): ('esc_dispatch', StateTransition('GROUND')),
        0x59: ('esc_dispatch', StateTransition('GROUND')),
        0x5a: ('esc_dispatch', StateTransition('GROUND')),
        0x5c: ('esc_dispatch', StateTransition('GROUND')),
        range(0x60, 0x7f): ('esc_dispatch', StateTransition('GROUND')),
        0x5b: StateTransition('CSI_ENTRY'),
        0x5d: StateTransition('OSC_STRING'),
        0x50: StateTransition('DCS_ENTRY'),
        0x58: StateTransition('SOS_PM_APC_STRING'),
        0x5e: StateTransition('SOS_PM_APC_STRING'),
        0x5f: StateTransition('SOS_PM_APC_STRING'),
    },

    'ESCAPE_INTERMEDIATE': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x20, 0x30): 'collect',
        0x7f: 'ignore',
        range(0x30, 0x7f): ('esc_dispatch', StateTransition('GROUND')),
    },

    'CSI_ENTRY': {
        'on_entry': 'clear',
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        0x7f: 'ignore',
        range(0x20, 0x30): ('collect', StateTransition('CSI_INTERMEDIATE')),
        0x3a: StateTransition('CSI_IGNORE'),
        range(0x30, 0x3a): ('param', StateTransition('CSI_PARAM')),
        0x3b: ('param', StateTransition('CSI_PARAM')),
        range(0x3c, 0x40): ('collect', StateTransition('CSI_PARAM')),
        range(0x40, 0x7f): ('csi_dispatch', StateTransition('GROUND')),
    },

    'CSI_IGNORE': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x20, 0x40): 'ignore',
        0x7f: 'ignore',
        range(0x40, 0x7f): StateTransition('GROUND'),
    },

    'CSI_PARAM': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x30, 0x3a): 'param',
        0x3b: 'param',
        0x7f: 'ignore',
        0x3a: StateTransition('CSI_IGNORE'),
        range(0x3c, 0x40): StateTransition('CSI_IGNORE'),
        range(0x20, 0x30): ('collect', StateTransition('CSI_INTERMEDIATE')),
        range(0x40, 0x7f): ('csi_dispatch', StateTransition('GROUND')),
    },

    'CSI_INTERMEDIATE': {
        range(0x18): 'execute',
        0x19: 'execute',
        range(0x1c, 0x20): 'execute',
        range(0x20, 0x30): 'collect',
        0x7f: 'ignore',
        range(0x30, 0x40): StateTransition('CSI_IGNORE'),
        range(0x40, 0x7f): ('csi_dispatch', StateTransition('GROUND')),
    },

    'DCS_ENTRY': {
        'on_entry': 'clear',
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x20): 'ignore',
        0x7f: 'ignore',
        0x3a: StateTransition('DCS_IGNORE'),
        range(0x20, 0x30): ('collect', StateTransition('DCS_INTERMEDIATE')),
        range(0x30, 0x3a): ('param', StateTransition('DCS_PARAM')),
        0x3b: ('param', StateTransition('DCS_PARAM')),
        range(0x3c, 0x40): ('collect', StateTransition('DCS_PARAM')),
        range(0x40, 0x7f): (StateTransition('DCS_PASSTHROUGH')),
    },

    'DCS_INTERMEDIATE': {
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x20): 'ignore',
        range(0x20, 0x30): 'collect',
        0x7f: 'ignore',
        range(0x30, 0x40): StateTransition('DCS_IGNORE'),
        range(0x40, 0x7f): StateTransition('DCS_PASSTHROUGH'),
    },

    'DCS_IGNORE': {
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x80): 'ignore',
    },

    'DCS_PARAM': {
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x20): 'ignore',
        range(0x30, 0x3a): 'param',
        0x3b: 'param',
        0x7f: 'ignore',
        0x3a: StateTransition('DCS_IGNORE'),
        range(0x3c, 0x40): StateTransition('DCS_IGNORE'),
        range(0x20, 0x30): ('collect', StateTransition('DCS_INTERMEDIATE')),
        range(0x40, 0x7f): StateTransition('DCS_PASSTHROUGH'),
    },

    'DCS_PASSTHROUGH': {
        'on_entry': 'hook',
        range(0x18): 'put',
        0x19: 'put',
        range(0x1c, 0x20): 'put',
        range(0x20, 0x7f): 'put',
        0x7f: 'ignore',
        'on_exit': 'unhook',
    },

    'SOS_PM_APC_STRING': {
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x80): 'ignore',
    },

    'OSC_STRING': {
        'on_entry': 'osc_start',
        range(0x18): 'ignore',
        0x19: 'ignore',
        range(0x1c, 0x20): 'ignore',
        range(0x20, 0x80): 'osc_put',
        'on_exit': 'osc_end',
    },
}


ACTIONS_IN_ORDER = sorted(
    action
    for state, transitions in STATES.items()
    for keys, actions in transitions.items()
    for action in ([actions] if not isinstance(actions, tuple) else actions)
    if isinstance(action, str)
)

STATES_IN_ORDER = sorted(STATES)


def _build_state_tables() -> ta.Mapping[str, ta.Sequence]:
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

    for state, transitions in STATES.items():
        state_tables[state] = expand_ranges(transitions)

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
        state: tuple(t if isinstance(t, tuple) else [t] for t in transitions)
        for state, transitions in state_tables.items()
    }


STATE_TABLES = _build_state_tables()


##


def _check_table() -> None:
    for state, transitions in STATE_TABLES.items():
        for i, val in enumerate(transitions):
            if not val:
                raise ValueError(f'No transition defined from state {state}, char 0x{i:02x}!')

    print('Tables had all necessary transitions defined.')


def _pad(s: str, length: int) -> str:
    return s + ' ' * (length - len(s))


def _generate_c() -> dict[str, str]:
    out = {}

    #

    import io
    f = io.StringIO()

    f.write('typedef enum {\n')
    for i, state in enumerate(STATES_IN_ORDER):
        f.write(f'   VTPARSE_STATE_{state.upper()} = {i + 1},\n')
    f.write('} vtparse_state_t;\n\n')

    f.write('typedef enum {\n')
    for i, action in enumerate(ACTIONS_IN_ORDER):
        f.write(f'   VTPARSE_ACTION_{action.upper()} = {i + 1},\n')
    f.write('} vtparse_action_t;\n\n')

    f.write('typedef unsigned char state_change_t;\n')
    f.write(f'extern state_change_t STATE_TABLE[{len(STATES_IN_ORDER)}][256];\n')
    f.write(f'extern vtparse_action_t ENTRY_ACTIONS[{len(STATES_IN_ORDER)}];\n')
    f.write(f'extern vtparse_action_t EXIT_ACTIONS[{len(STATES_IN_ORDER)}];\n')
    f.write(f'extern char *ACTION_NAMES[{len(ACTIONS_IN_ORDER) + 1}];\n')
    f.write(f'extern char *STATE_NAMES[{len(STATES_IN_ORDER) + 1}];\n\n')

    out['vtparse_table.h'] = f.getvalue()

    #

    f = io.StringIO()

    f.write('#include "vtparse_table.h"\n\n')

    f.write('char *ACTION_NAMES[] = {\n')
    f.write('   "<no action>",\n')
    for action in ACTIONS_IN_ORDER:
        f.write(f'   "{action.upper()}",\n')
    f.write('};\n\n')

    f.write('char *STATE_NAMES[] = {\n')
    f.write('   "<no state>",\n')
    for state in STATES_IN_ORDER:
        f.write(f'   "{state}",\n')
    f.write('};\n\n')

    f.write(f'state_change_t STATE_TABLE[{len(STATES_IN_ORDER)}][256] = {{\n')
    for i, state in enumerate(STATES_IN_ORDER):
        f.write(f'  {{  /* VTPARSE_STATE_{state.upper()} = {i} */\n')
        for j, state_change in enumerate(STATE_TABLES[state]):
            if not state_change:
                f.write('    0,\n')
            else:
                action = next((s for s in state_change if isinstance(s, str)), None)
                state_trans = next((s for s in state_change if isinstance(s, StateTransition)), None)
                action_str = f'VTPARSE_ACTION_{action.upper()}' if action else '0'
                state_str = f'VTPARSE_STATE_{state_trans.to_state}' if state_trans else '0'
                f.write(
                    f'/*{str(j).rjust(3)}*/  {_pad(action_str, 33)} | ({_pad(state_str, 33)} << 4),\n')
        f.write('  },\n')
    f.write('};\n\n')

    f.write('vtparse_action_t ENTRY_ACTIONS[] = {\n')
    for state in STATES_IN_ORDER:
        actions = STATES[state]
        if 'on_entry' in actions:
            f.write(f"   VTPARSE_ACTION_{actions['on_entry'].upper()}, /* {state} */\n")
        else:
            f.write(f'   0  /* none for {state} */,\n')
    f.write('};\n\n')

    f.write('vtparse_action_t EXIT_ACTIONS[] = {\n')
    for state in STATES_IN_ORDER:
        actions = STATES[state]
        if 'on_exit' in actions:
            f.write(f"   VTPARSE_ACTION_{actions['on_exit'].upper()}, /* {state} */\n")
        else:
            f.write(f'   0  /* none for {state} */,\n')
    f.write('};\n\n')

    out['vtparse_table.c'] = f.getvalue()

    #

    return out


if __name__ == '__main__':
    _check_table()
    _generate_c()
