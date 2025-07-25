import os.path
import typing as ta

from omlish import check
from omlish.formats import json

from ..rendering import LsLinesRenderer
from ..running import LsRunner


def test_ls():
    root_dir = os.path.join(os.path.dirname(__file__), 'root')

    root = LsRunner().run(root_dir)
    lines = LsLinesRenderer().render(root)
    print('\n'.join(lines.lines))


def execute_ls_tool(
        base_path: str,
) -> str:
    """
    Recursively lists the directory contents of the given base path.

    Args:
        base_path: The path of the directory to list the contents of.

    Returns:
        A formatted string of the recursive directory contents.
    """

    root = LsRunner().run(base_path)
    lines = LsLinesRenderer().render(root)
    return '\n'.join(lines.lines)


def test_ls_tool():
    from .....tools.reflect import reflect_tool_spec
    tool_spec = reflect_tool_spec(execute_ls_tool)
    print(tool_spec)

    from .....tools.jsonschema import build_tool_spec_json_schema
    print(build_tool_spec_json_schema(tool_spec))

    root_dir = os.path.join(os.path.dirname(__file__), 'root')
    tool_args = {
        'base_path': root_dir,
    }

    from .....chat.messages import ToolExecRequest
    tool_exec_request = ToolExecRequest(
        'foo_id',
        tool_spec,
        tool_args,
    )

    result_obj: ta.Any = execute_ls_tool(**tool_args)

    result_str: str
    if isinstance(result_obj, str):
        result_str = result_obj
    else:
        result_str = json.dumps_compact(result_obj)

    from .....chat.messages import ToolExecResultMessage
    tool_exec_result = ToolExecResultMessage(
        tool_exec_request.id,
        check.not_none(tool_spec.name),
        result_str,
    )

    print(tool_exec_result)
