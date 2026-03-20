import os.path

import pytest

from .....tools.execution.context import bind_tool_context
from ...context import FsContext
from ..ls import execute_ls_tool


@pytest.mark.asyncs('asyncio')
async def test_ls():
    with bind_tool_context(FsContext(root_dir=os.path.dirname(__file__))):
        print()
        print(await execute_ls_tool(os.path.dirname(__file__)))
