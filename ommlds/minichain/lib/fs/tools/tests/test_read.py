import os.path

from .....tools.execution.context import bind_tool_context
from ...context import FsContext
from ..read import execute_read_tool


def test_read():
    with bind_tool_context(FsContext(root_dir=os.path.dirname(__file__))):
        print()
        print(execute_read_tool(__file__, line_offset=8, num_lines=3))
