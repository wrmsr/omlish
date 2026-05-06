import os.path

import pytest

from .....tools.execution.context import activate_tool_context
from .....tools.execution.permissions import StaticToolPermissionDecider
from .....tools.permissions.types import ToolPermissionState
from ...context import FsContext
from ..ls import ls


@pytest.mark.asyncs('asyncio')
async def test_ls():
    with activate_tool_context(
            StaticToolPermissionDecider(ToolPermissionState.ALLOW),
            FsContext(root_dir=os.path.dirname(__file__)),
    ):
        print()
        print(await ls(os.path.dirname(__file__)))
