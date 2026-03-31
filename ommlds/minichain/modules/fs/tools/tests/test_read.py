import os.path

import pytest

from .....tools.execution.context import bind_tool_context
from .....tools.execution.permissions import StaticToolPermissionDecider
from .....tools.permissions.types import ToolPermissionState
from ...context import FsContext
from ..read import execute_read_tool


@pytest.mark.asyncs('asyncio')
async def test_read():
    with bind_tool_context(
            StaticToolPermissionDecider(ToolPermissionState.ALLOW),
            FsContext(root_dir=os.path.dirname(__file__)),
    ):
        print()
        print(await execute_read_tool(__file__, line_offset=8, num_lines=3))
