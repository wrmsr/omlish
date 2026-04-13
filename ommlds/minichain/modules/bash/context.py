import os.path

from ...tools.execution.context import tool_context
from ...tools.execution.permissions import tool_permission_decider
from ...tools.permissions.bash import BashToolPermissionTarget


##


class BashContext:
    def __init__(
            self,
            *,
            root_dir: str | None = None,
    ) -> None:
        super().__init__()

        self._root_dir = root_dir

        self._abs_root_dir = os.path.abspath(root_dir) if root_dir is not None else None

    #

    async def check_cmd_permitted(self, cmd: str) -> None:
        await tool_permission_decider().check_allowed(BashToolPermissionTarget(cmd))


def tool_bash_context() -> BashContext:
    return tool_context()[BashContext]
