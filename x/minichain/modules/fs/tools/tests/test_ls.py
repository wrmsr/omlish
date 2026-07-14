import os.path

import pytest

from omcore import contextual as cxl

from .....fs.types import FsRoot
from .....tools.execution.permissions import StaticToolPermissionDecider
from .....tools.permissions.types import ToolPermissionState
from ...context import FsContext
from ..ls import ls
from ..ls import ls_tool


@pytest.mark.asyncs('asyncio')
async def test_ls_kw():
    print()
    print(await ls(
        os.path.dirname(__file__),
        ctx=FsContext(
            root_dir=FsRoot(os.path.dirname(__file__)),
            tool_permission_decider=StaticToolPermissionDecider(ToolPermissionState.ALLOW),
        ),
    ))


@pytest.mark.asyncs('asyncio')
async def test_ls_cxl():
    with cxl.bind({
        FsContext: FsContext(
            root_dir=FsRoot(os.path.dirname(__file__)),
            tool_permission_decider=StaticToolPermissionDecider(ToolPermissionState.ALLOW),
        ),
    }):
        print()
        print(await ls(os.path.dirname(__file__)))


def test_reflect():
    print(ls_tool())
