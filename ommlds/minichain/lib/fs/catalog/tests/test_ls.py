import os.path

from .....tools.execution.context import bind_tool_context
from ...context import FsToolContext
from ..ls import execute_ls_tool


def test_ls():
    with bind_tool_context(FsToolContext(root_dir=os.path.dirname(__file__))):
        print()
        print(execute_ls_tool(os.path.dirname(__file__)))
