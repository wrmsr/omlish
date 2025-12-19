from omlish.formats import json

from ...... import minichain as mc
from ...drivers.tools.confirmation import ToolExecutionConfirmation
from ...drivers.tools.confirmation import ToolExecutionRequestDeniedError
from .app import ChatAppGetter


##


class ChatAppToolExecutionConfirmation(ToolExecutionConfirmation):
    def __init__(
            self,
            *,
            app: ChatAppGetter,
    ) -> None:
        super().__init__()

        self._app = app

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

        if not await (await self._app()).confirm_tool_use(
                'Execute requested tool?',
                json.dumps_pretty(tr_dct),
        ):
            raise ToolExecutionRequestDeniedError
