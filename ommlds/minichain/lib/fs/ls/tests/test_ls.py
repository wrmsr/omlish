import os.path
import typing as ta

from omlish import check

from ..rendering import LsLinesRenderer
from ..running import LsRunner
from .newtools import ToolExecutor


def test_ls():
    root_dir = os.path.join(os.path.dirname(__file__), 'root')

    root = LsRunner().run(root_dir)
    lines = LsLinesRenderer().render(root)
    print('\n'.join(lines.lines))


def execute_tool_executor(
        te: ToolExecutor,
        args: ta.Mapping[str, ta.Any],
) -> str:
    fn = te.fn

    out: ta.Any
    if isinstance(te.input, ToolExecutor.DataclassInput):
        raise NotImplementedError
    elif isinstance(te.input, ToolExecutor.KwargsInput):
        out = fn(**args)
    else:
        raise NotImplementedError

    ret: str
    if isinstance(te.output, ToolExecutor.DataclassOutput):
        raise NotImplementedError
    elif isinstance(te.output, ToolExecutor.RawStringOutput):
        ret = check.isinstance(out, str)
    else:
        raise NotImplementedError

    return ret


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

    ls_tool_executor = ToolExecutor(
        execute_ls_tool,
        ToolExecutor.KwargsInput(),
        ToolExecutor.RawStringOutput(),
    )

    result_str = execute_tool_executor(
        ls_tool_executor,
        tool_args,
    )

    from .....chat.messages import ToolExecResultMessage
    tool_exec_result = ToolExecResultMessage(
        tool_exec_request.id,
        check.not_none(tool_spec.name),
        result_str,
    )

    print(tool_exec_result)
