from omlish.formats import json

from ...... import minichain as mc
from ...drivers.tools.confirmation import ToolExecutionConfirmation
from ...drivers.tools.confirmation import ToolExecutionRequestDeniedError


##


class ChatAppToolExecutionConfirmation(ToolExecutionConfirmation):
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

        msg = f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}'  # noqa

        raise ToolExecutionRequestDeniedError
