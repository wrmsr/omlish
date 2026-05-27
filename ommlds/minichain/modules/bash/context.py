import os.path

from ...fs import FsRoot
from ...tools.execution.permissions import DENY_TOOL_PERMISSION_DECIDER
from ...tools.execution.permissions import ToolPermissionDecider
from ...tools.permissions.bash import BashToolPermissionTarget


##


class BashContext:
    def __init__(
            self,
            *,
            root_dir: FsRoot | None = None,
            tool_permission_decider: ToolPermissionDecider = DENY_TOOL_PERMISSION_DECIDER,
    ) -> None:
        super().__init__()

        self._root_dir = root_dir
        self._tool_permission_decider = tool_permission_decider

        self._abs_root_dir = os.path.abspath(root_dir) if root_dir is not None else None

    #

    async def check_cmd_permitted(self, cmd: str) -> None:
        await self._tool_permission_decider.check_allowed(BashToolPermissionTarget(cmd))
