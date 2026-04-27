from omlish.formats import json

from ...... import minichain as mc
from .types import ChatDriverInterfaceGetter


##


class ChatAppToolPermissionConfirmation(mc.drivers.ToolPermissionConfirmation):
    def __init__(
            self,
            *,
            chat_driver_interface: ChatDriverInterfaceGetter,
    ) -> None:
        super().__init__()

        self._chat_driver_interface = chat_driver_interface

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

        if await (await self._chat_driver_interface()).confirm_tool_use(
                'Execute requested tool?',
                json.dumps_pretty(tr_dct),
        ):
            return mc.ToolPermissionState.ALLOW
        else:
            return mc.ToolPermissionState.DENY
