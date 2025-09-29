import os.path

from omlish import check
from omlish import lang

from ......chat.messages import ToolUse
from ......chat.tools.execution import execute_tool_use
from ......tools.execution.context import ToolContext
from ......tools.execution.executors import NameSwitchedToolExecutor
from ......tools.jsonschema import build_tool_spec_json_schema
from ....context import FsContext
from ..execution import recursive_ls_tool


##


def test_recursive_ls_tool():
    rlt = recursive_ls_tool()

    print(rlt.spec)

    print(build_tool_spec_json_schema(rlt.spec))

    root_dir = os.path.join(os.path.dirname(__file__), 'root')

    tool_args = {
        'base_path': root_dir,
    }

    tool_exec_request = ToolUse(
        id='foo_id',
        name=check.not_none(rlt.spec.name),
        args=tool_args,
    )

    tool_executor = NameSwitchedToolExecutor({
        check.not_none(rlt.name): rlt.executor(),
    })

    tool_exec_result = lang.run_maysync(execute_tool_use(
        ToolContext(
            tool_exec_request,
            FsContext(root_dir=root_dir),
        ),
        tool_executor,
        tool_exec_request,
    ))

    print()
    print(tool_exec_result.tur.c)
