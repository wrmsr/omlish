from omlish.formats import json
from omlish.term.confirm import confirm_action

from ...... import minichain as mc
from ...drivers.tools.confirmation import ToolExecutionConfirmation
from ...drivers.tools.confirmation import ToolExecutionRequestDeniedError


##


class InteractiveToolExecutionConfirmation(ToolExecutionConfirmation):
    async def confirm_tool_execution_or_raise(
            self,
            use: 'mc.ToolUse',
            entry: 'mc.ToolCatalogEntry',
    ) -> None:
        tr_dct = dict(
            id=use.id,
            name=entry.spec.name,
            args=use.args,
            # spec=msh.marshal(tce.spec),
        )
        cr = confirm_action(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}')  # FIXME: async lol

        if not cr:
            raise ToolExecutionRequestDeniedError
