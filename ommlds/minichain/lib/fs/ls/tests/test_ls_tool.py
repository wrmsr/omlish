import os.path

from omlish import check

from .....chat.messages import ToolExecRequest
from .....chat.messages import ToolExecResultMessage
from .....content.namespaces import ContentNamespace
from .....tools.jsonschema import build_tool_spec_json_schema
from .....tools.reflect import reflect_tool_spec
from .....tools.reflect import tool_spec_override
from ..rendering import LsLinesRenderer
from ..running import LsRunner
from .newtools import ToolContext
from .newtools import ToolExecutor
from .newtools import execute_tool_executor


class LsDescription(ContentNamespace):
    SUMMARY = """
    Recursively lists the directory contents of the given base path.
    """


@tool_spec_override(desc=LsDescription)
def execute_ls_tool(
        base_path: str,
) -> str:
    """
    Args:
        base_path: The path of the directory to list the contents of.

    Returns:
        A formatted string of the recursive directory contents.
    """

    root = LsRunner().run(base_path)
    lines = LsLinesRenderer().render(root)
    return '\n'.join(lines.lines)


def test_ls_tool():
    tool_spec = reflect_tool_spec(execute_ls_tool)
    print(tool_spec)

    print(build_tool_spec_json_schema(tool_spec))

    root_dir = os.path.join(os.path.dirname(__file__), 'root')
    tool_args = {
        'base_path': root_dir,
    }

    tool_exec_request = ToolExecRequest(
        'foo_id',
        tool_spec,
        tool_args,
    )

    ls_tool_executor = ToolExecutor(
        execute_ls_tool,
        ToolExecutor.KwargsInput(),
        ToolExecutor.RawStringOutput(),
    )

    tc = ToolContext()

    result_str = execute_tool_executor(
        tc,
        ls_tool_executor,
        tool_args,
    )

    tool_exec_result = ToolExecResultMessage(
        tool_exec_request.id,
        check.not_none(tool_spec.name),
        result_str,
    )

    print(tool_exec_result)
