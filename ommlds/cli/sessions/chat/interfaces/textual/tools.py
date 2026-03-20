from omlish.formats import json

from ...... import minichain as mc
from .types import ChatAppGetter


##


class ChatAppToolExecutionConfirmation(mc.drivers.ToolExecutionConfirmation):
    def __init__(
            self,
            *,
            app: ChatAppGetter,
    ) -> None:
        super().__init__()

        self._app = app

    async def confirm_tool_execution_or_raise(self, tue: 'mc.drivers.ToolUseExecution') -> None:
        tr_dct = dict(
            id=tue.use.id,
            name=tue.tce.spec.name,
            args=tue.use.args,
            # spec=msh.marshal(tce.spec),
        )

        if not await (await self._app()).confirm_tool_use(
                'Execute requested tool?',
                json.dumps_pretty(tr_dct),
        ):
            raise mc.drivers.ToolExecutionRequestDeniedError
