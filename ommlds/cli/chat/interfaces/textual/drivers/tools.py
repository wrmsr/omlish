from omdev.tui import textual as tx
from omlish import check
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
            tue: mc.ToolUseExecution,
            target: mc.ToolPermissionTarget,
    ) -> mc.DecidedToolPermissionState:
        tr_dct = dict(
            id=tue.use.id,
            name=check.not_none(tue.catalog_entry).spec.name,
            args=tue.use.args,
            # spec=msh.marshal(tce.spec),
        )

        if await (await self._chat_driver_interface()).confirm_tool_use(
                tx.Text('Execute requested tool?'),
                tx.Text(json.dumps_pretty(tr_dct)),
        ):
            return mc.ToolPermissionState.ALLOW
        else:
            return mc.ToolPermissionState.DENY
