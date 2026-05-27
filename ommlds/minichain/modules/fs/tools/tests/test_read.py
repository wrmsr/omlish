import os.path

import pytest

from .....fs import FsRoot
from .....tools.execution.permissions import StaticToolPermissionDecider
from .....tools.permissions.types import ToolPermissionState
from ...context import FsContext
from ..read import read_file


@pytest.mark.asyncs('asyncio')
async def test_read():
    print()
    print(await read_file(
        __file__,
        line_offset=8,
        num_lines=3,

        ctx=FsContext(
            root_dir=FsRoot(os.path.dirname(__file__)),
            tool_permission_decider=StaticToolPermissionDecider(ToolPermissionState.ALLOW),
        ),
    ))
