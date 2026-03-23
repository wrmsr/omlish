from omlish.formats import json

from ...... import minichain as mc
from .types import ChatAppGetter


##


class ChatAppToolPermissionConfirmation(mc.drivers.ToolPermissionConfirmation):
    def __init__(
            self,
            *,
            app: ChatAppGetter,
    ) -> None:
        super().__init__()

        self._app = app

    async def confirm_tool_permission(
            self,
            tue: mc.drivers.ToolUseExecution,
            target: mc.ToolPermissionTarget,
    ) -> mc.DecidedToolPermissionState:
        tr_dct = dict(
            id=tue.use.id,
            name=tue.tce.spec.name,
            args=tue.use.args,
            # spec=msh.marshal(tce.spec),
        )

        if await (await self._app()).confirm_tool_use(
                'Execute requested tool?',
                json.dumps_pretty(tr_dct),
        ):
            return mc.ToolPermissionState.ALLOW
        else:
            return mc.ToolPermissionState.DENY
