import os.path

import pytest

from .....fs import FsRoot
from .....tools.execution.context import activate_tool_context
from .....tools.execution.permissions import StaticToolPermissionDecider
from .....tools.permissions.types import ToolPermissionState
from ...context import FsContext
from ..read import read_file


@pytest.mark.asyncs('asyncio')
async def test_read():
    with activate_tool_context(
            StaticToolPermissionDecider(ToolPermissionState.ALLOW),
            FsContext(root_dir=FsRoot(os.path.dirname(__file__))),
    ):
        print()
        print(await read_file(__file__, line_offset=8, num_lines=3))
