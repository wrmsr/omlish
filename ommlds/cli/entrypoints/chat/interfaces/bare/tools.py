from omlish.formats import json
from omlish.term.confirm import confirm_action

from ...... import minichain as mc


##


class InteractiveToolPermissionConfirmation(mc.drivers.ToolPermissionConfirmation):
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
        cr = confirm_action(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}')  # FIXME: async lol

        if cr:
            return mc.ToolPermissionState.ALLOW
        else:
            return mc.ToolPermissionState.DENY
