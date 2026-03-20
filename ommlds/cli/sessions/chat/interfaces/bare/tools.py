from omlish.formats import json
from omlish.term.confirm import confirm_action

from ...... import minichain as mc


##


class InteractiveToolExecutionConfirmation(mc.drivers.ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(self, tue: 'mc.drivers.ToolUseExecution') -> None:
        tr_dct = dict(
            id=tue.use.id,
            name=tue.tce.spec.name,
            args=tue.use.args,
            # spec=msh.marshal(tce.spec),
        )
        cr = confirm_action(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}')  # FIXME: async lol

        if not cr:
            raise mc.drivers.ToolExecutionRequestDeniedError
