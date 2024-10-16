"""
https://vt100.net/emu/dec_ansi_parser

https://github.com/haberman/vtparse

==

https://github.com/alacritty/vte/blob/master/src/ansi.rs
https://crates.io/crates/vt100
"""
##
# Original author: Joshua Haberman
# https://github.com/haberman/vtparse/blob/198ea4382f824dbb3f0e5b5553a9eb3290764694/vtparse_tables.rb


class StateTransition:
    def __init__(self, to_state):
        self.to_state = to_state


def transition_to(state):
    return StateTransition(state)


# Global states dictionary
states = {}

# Define the anywhere transitions
anywhere_transitions = {
    0x18: ['execute', transition_to('GROUND')],
    0x1a: ['execute', transition_to('GROUND')],
    range(0x80, 0x90): ['execute', transition_to('GROUND')],
    range(0x91, 0x98): ['execute', transition_to('GROUND')],
    0x99: ['execute', transition_to('GROUND')],
    0x9a: ['execute', transition_to('GROUND')],
    0x9c: transition_to('GROUND'),
    0x1b: transition_to('ESCAPE'),
    0x98: transition_to('SOS_PM_APC_STRING'),
    0x9e: transition_to('SOS_PM_APC_STRING'),
    0x9f: transition_to('SOS_PM_APC_STRING'),
    0x90: transition_to('DCS_ENTRY'),
    0x9d: transition_to('OSC_STRING'),
    0x9b: transition_to('CSI_ENTRY'),
}

# Define state transitions
states['GROUND'] = {
    range(0x18): 'execute',
    0x19: 'execute',
    range(0x1c, 0x20): 'execute',
    range(0x20, 0x80): 'print',
}

states['ESCAPE'] = {
    'on_entry': 'clear',
    range(0x18): 'execute',
    0x19: 'execute',
    range(0x1c, 0x20): 'execute',
    0x7f: 'ignore',
    range(0x20, 0x30): ['collect', transition_to('ESCAPE_INTERMEDIATE')],
    range(0x30, 0x50): ['esc_dispatch', transition_to('GROUND')],
    range(0x51, 0x58): ['esc_dispatch', transition_to('GROUND')],
    0x59: ['esc_dispatch', transition_to('GROUND')],
    0x5a: ['esc_dispatch', transition_to('GROUND')],
    0x5c: ['esc_dispatch', transition_to('GROUND')],
    range(0x60, 0x7f): ['esc_dispatch', transition_to('GROUND')],
    0x5b: transition_to('CSI_ENTRY'),
    0x5d: transition_to('OSC_STRING'),
    0x50: transition_to('DCS_ENTRY'),
    0x58: transition_to('SOS_PM_APC_STRING'),
    0x5e: transition_to('SOS_PM_APC_STRING'),
    0x5f: transition_to('SOS_PM_APC_STRING'),
}

states['ESCAPE_INTERMEDIATE'] = {
    range(0x18): 'execute',
    0x19: 'execute',
    range(0x1c, 0x20): 'execute',
    range(0x20, 0x30): 'collect',
    0x7f: 'ignore',
    range(0x30, 0x7f): ['esc_dispatch', transition_to('GROUND')],
}

states['CSI_ENTRY'] = {
    'on_entry': 'clear',
    range(0x18): 'execute',
    0x19: 'execute',
    range(0x1c, 0x20): 'execute',
    0x7f: 'ignore',
    range(0x20, 0x30): ['collect', transition_to('CSI_INTERMEDIATE')],
    0x3a: transition_to('CSI_IGNORE'),
    range(0x30, 0x3a): ['param', transition_to('CSI_PARAM')],
    0x3b: ['param', transition_to('CSI_PARAM')],
    range(0x3c, 0x40): ['collect', transition_to('CSI_PARAM')],
    range(0x40, 0x7f): ['csi_dispatch', transition_to('GROUND')],
}

states['CSI_IGNORE'] = {
    range(0x18): 'execute',
    0x19: 'execute',
    range(0x1c, 0x20): 'execute',
    range(0x20, 0x40): 'ignore',
    0x7f: 'ignore',
    range(0x40, 0x7f): transition_to('GROUND'),
}

states['CSI_PARAM'] = {
    range(0x18): 'execute',
    0x19: 'execute',
    range(0x1c, 0x20): 'execute',
    range(0x30, 0x3a): 'param',
    0x3b: 'param',
    0x7f: 'ignore',
    0x3a: transition_to('CSI_IGNORE'),
    range(0x3c, 0x40): transition_to('CSI_IGNORE'),
    range(0x20, 0x30): ['collect', transition_to('CSI_INTERMEDIATE')],
    range(0x40, 0x7f): ['csi_dispatch', transition_to('GROUND')],
}

states['CSI_INTERMEDIATE'] = {
    range(0x18): 'execute',
    0x19: 'execute',
    range(0x1c, 0x20): 'execute',
    range(0x20, 0x30): 'collect',
    0x7f: 'ignore',
    range(0x30, 0x40): transition_to('CSI_IGNORE'),
    range(0x40, 0x7f): ['csi_dispatch', transition_to('GROUND')],
}

states['DCS_ENTRY'] = {
    'on_entry': 'clear',
    range(0x18): 'ignore',
    0x19: 'ignore',
    range(0x1c, 0x20): 'ignore',
    0x7f: 'ignore',
    0x3a: transition_to('DCS_IGNORE'),
    range(0x20, 0x30): ['collect', transition_to('DCS_INTERMEDIATE')],
    range(0x30, 0x3a): ['param', transition_to('DCS_PARAM')],
    0x3b: ['param', transition_to('DCS_PARAM')],
    range(0x3c, 0x40): ['collect', transition_to('DCS_PARAM')],
    range(0x40, 0x7f): [transition_to('DCS_PASSTHROUGH')],
}

states['DCS_INTERMEDIATE'] = {
    range(0x18): 'ignore',
    0x19: 'ignore',
    range(0x1c, 0x20): 'ignore',
    range(0x20, 0x30): 'collect',
    0x7f: 'ignore',
    range(0x30, 0x40): transition_to('DCS_IGNORE'),
    range(0x40, 0x7f): transition_to('DCS_PASSTHROUGH'),
}

states['DCS_IGNORE'] = {
    range(0x18): 'ignore',
    0x19: 'ignore',
    range(0x1c, 0x80): 'ignore',
}

states['DCS_PARAM'] = {
    range(0x18): 'ignore',
    0x19: 'ignore',
    range(0x1c, 0x20): 'ignore',
    range(0x30, 0x3a): 'param',
    0x3b: 'param',
    0x7f: 'ignore',
    0x3a: transition_to('DCS_IGNORE'),
    range(0x3c, 0x40): transition_to('DCS_IGNORE'),
    range(0x20, 0x30): ['collect', transition_to('DCS_INTERMEDIATE')],
    range(0x40, 0x7f): transition_to('DCS_PASSTHROUGH'),
}

states['DCS_PASSTHROUGH'] = {
    'on_entry': 'hook',
    range(0x18): 'put',
    0x19: 'put',
    range(0x1c, 0x20): 'put',
    range(0x20, 0x7f): 'put',
    0x7f: 'ignore',
    'on_exit': 'unhook',
}

states['SOS_PM_APC_STRING'] = {
    range(0x18): 'ignore',
    0x19: 'ignore',
    range(0x1c, 0x80): 'ignore',
}

states['OSC_STRING'] = {
    'on_entry': 'osc_start',
    range(0x18): 'ignore',
    0x19: 'ignore',
    range(0x1c, 0x20): 'ignore',
    range(0x20, 0x80): 'osc_put',
    'on_exit': 'osc_end',
}

# Get the list of actions implicit in the tables
action_names = {}
for state, transitions in states.items():
    for keys, actions in transitions.items():
        if not isinstance(actions, list):
            actions = [actions]
        for action in actions:
            if isinstance(action, str):
                action_names[action] = 1

# Establish an ordering to the states and actions
actions_in_order = sorted(action_names.keys()) + ['error']
states_in_order = sorted(states.keys())

# Expand the range-based data structures into fully expanded tables
state_tables = {}


def expand_ranges(hash_with_ranges_as_keys):
    array = [None] * 256
    for k, v in hash_with_ranges_as_keys.items():
        if isinstance(k, range):
            for i in k:
                array[i] = v
        elif isinstance(k, int):
            array[k] = v
    return array


for state, transitions in states.items():
    state_tables[state] = expand_ranges(transitions)

# Seed all the states with the anywhere transitions
anywhere_transitions_expanded = expand_ranges(anywhere_transitions)

for state, transitions in state_tables.items():
    for i, transition in enumerate(anywhere_transitions_expanded):
        if transition is not None:
            if transitions[i] is not None:
                raise ValueError(
                    f'State {state} already had a transition defined for 0x{i:02x}, but that transition is also an '
                    f'anywhere transition!',
                )
            transitions[i] = transition

# For consistency, make all transitions lists of actions
for state, transitions in state_tables.items():
    state_tables[state] = [t if isinstance(t, list) else [t] for t in transitions]


def _check_table():
    for state, transitions in state_tables.items():
        for i, val in enumerate(transitions):
            if not val:
                raise ValueError(f'No transition defined from state {state}, char 0x{i:02x}!')

    print('Tables had all necessary transitions defined.')


def _pad(s, length):
    return s + ' ' * (length - len(s))


def _generate_c() -> dict[str, str]:
    out = {}

    #

    import io
    f = io.StringIO()

    f.write('typedef enum {\n')
    for i, state in enumerate(states_in_order):
        f.write(f'   VTPARSE_STATE_{state.upper()} = {i + 1},\n')
    f.write('} vtparse_state_t;\n\n')

    f.write('typedef enum {\n')
    for i, action in enumerate(actions_in_order):
        f.write(f'   VTPARSE_ACTION_{action.upper()} = {i + 1},\n')
    f.write('} vtparse_action_t;\n\n')

    f.write('typedef unsigned char state_change_t;\n')
    f.write(f'extern state_change_t STATE_TABLE[{len(states_in_order)}][256];\n')
    f.write(f'extern vtparse_action_t ENTRY_ACTIONS[{len(states_in_order)}];\n')
    f.write(f'extern vtparse_action_t EXIT_ACTIONS[{len(states_in_order)}];\n')
    f.write(f'extern char *ACTION_NAMES[{len(actions_in_order) + 1}];\n')
    f.write(f'extern char *STATE_NAMES[{len(states_in_order) + 1}];\n\n')

    out['vtparse_table.h'] = f.getvalue()

    #

    f = io.StringIO()

    f.write('#include "vtparse_table.h"\n\n')

    f.write('char *ACTION_NAMES[] = {\n')
    f.write('   "<no action>",\n')
    for action in actions_in_order:
        f.write(f'   "{action.upper()}",\n')
    f.write('};\n\n')

    f.write('char *STATE_NAMES[] = {\n')
    f.write('   "<no state>",\n')
    for state in states_in_order:
        f.write(f'   "{state}",\n')
    f.write('};\n\n')

    f.write(f'state_change_t STATE_TABLE[{len(states_in_order)}][256] = {{\n')
    for i, state in enumerate(states_in_order):
        f.write(f'  {{  /* VTPARSE_STATE_{state.upper()} = {i} */\n')
        for j, state_change in enumerate(state_tables[state]):
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
    for state in states_in_order:
        actions = states[state]
        if 'on_entry' in actions:
            f.write(f"   VTPARSE_ACTION_{actions['on_entry'].upper()}, /* {state} */\n")
        else:
            f.write(f'   0  /* none for {state} */,\n')
    f.write('};\n\n')

    f.write('vtparse_action_t EXIT_ACTIONS[] = {\n')
    for state in states_in_order:
        actions = states[state]
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
