import os.path

import pytest

from .....fs import FsRoot
from .....tools.execution.context import activate_tool_context
from .....tools.execution.permissions import StaticToolPermissionDecider
from .....tools.permissions.types import ToolPermissionState
from ...context import FsContext
from ..ls import ls
from ..ls import ls_tool


@pytest.mark.asyncs('asyncio')
async def test_ls():
    with activate_tool_context(
            StaticToolPermissionDecider(ToolPermissionState.ALLOW),
            FsContext(root_dir=FsRoot(os.path.dirname(__file__))),
    ):
        print()
        print(await ls(os.path.dirname(__file__)))


def test_reflect():
    print(ls_tool())
