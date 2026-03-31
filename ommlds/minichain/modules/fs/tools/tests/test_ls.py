import os.path

import pytest

from .....tools.execution.context import bind_tool_context
from .....tools.execution.permissions import StaticToolPermissionDecider
from .....tools.permissions.types import ToolPermissionState
from ...context import FsContext
from ..ls import execute_ls_tool


@pytest.mark.asyncs('asyncio')
async def test_ls():
    with bind_tool_context(
            StaticToolPermissionDecider(ToolPermissionState.ALLOW),
            FsContext(root_dir=os.path.dirname(__file__)),
    ):
        print()
        print(await execute_ls_tool(os.path.dirname(__file__)))
