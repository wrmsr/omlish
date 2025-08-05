import os.path

from omlish import check

from .....chat.messages import ToolExecRequest
from .....chat.tools.execution import execute_tool_request
from .....tools.execution.context import ToolContext
from .....tools.execution.executors import NameSwitchedToolExecutor
from .....tools.jsonschema import build_tool_spec_json_schema
from ..execution import ls_tool


##


def test_ls_tool():
    print(ls_tool().spec)

    print(build_tool_spec_json_schema(ls_tool().spec))

    root_dir = os.path.join(os.path.dirname(__file__), 'root')
    tool_args = {
        'base_path': root_dir,
    }

    tool_exec_request = ToolExecRequest(
        id='foo_id',
        name=check.not_none(ls_tool().spec.name),
        args=tool_args,
    )

    tool_executor = NameSwitchedToolExecutor({
        check.not_none(ls_tool().name): ls_tool().executor(),
    })

    tool_exec_result = execute_tool_request(
        ToolContext.new(
            tool_exec_request,
        ),
        tool_executor,
        tool_exec_request,
    )

    print(tool_exec_result)
