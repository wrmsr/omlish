import io

from ... import check
from .states import ACTIONS_IN_ORDER
from .states import STATE_TABLES
from .states import STATES
from .states import STATES_IN_ORDER
from .states import StateTransition
from .states import check_state_tables


##


def _pad(s: str, length: int) -> str:
    return s + ' ' * (length - len(s))


def _generate_c() -> dict[str, str]:
    out = {}

    #

    f = io.StringIO()

    f.write('typedef enum {\n')
    for i, state in enumerate(STATES_IN_ORDER):
        f.write(f'   VTPARSE_STATE_{state.upper()} = {i + 1},\n')
    f.write('} vtparse_state_t;\n\n')

    f.write('typedef enum {\n')
    for i, action_str in enumerate(ACTIONS_IN_ORDER):
        f.write(f'   VTPARSE_ACTION_{action_str.upper()} = {i + 1},\n')
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
    for action_str in ACTIONS_IN_ORDER:
        f.write(f'   "{action_str.upper()}",\n')
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
            f.write(f"   VTPARSE_ACTION_{check.isinstance(actions['on_entry'], str).upper()}, /* {state} */\n")
        else:
            f.write(f'   0  /* none for {state} */,\n')
    f.write('};\n\n')

    f.write('vtparse_action_t EXIT_ACTIONS[] = {\n')
    for state in STATES_IN_ORDER:
        actions = STATES[state]
        if 'on_exit' in actions:
            f.write(f"   VTPARSE_ACTION_{check.isinstance(actions['on_exit'], str).upper()}, /* {state} */\n")
        else:
            f.write(f'   0  /* none for {state} */,\n')
    f.write('};\n\n')

    out['vtparse_table.c'] = f.getvalue()

    #

    return out


if __name__ == '__main__':
    check_state_tables(STATE_TABLES)
    for f, c in _generate_c().items():
        print(f)
        print(c)
        print()
