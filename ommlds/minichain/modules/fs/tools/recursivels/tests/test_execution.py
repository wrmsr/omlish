import os.path

import pytest

from omlish import check
from omlish import contextual as cxl

from ......chat.messages import ToolUse
from ......fs.types import FsRoot
from ......tools.execution.execution import execute_tool_use
from ......tools.execution.invokers import NameSwitchedToolInvoker
from ......tools.execution.permissions import StaticToolPermissionDecider
from ......tools.jsonschema import build_tool_spec_json_schema
from ......tools.permissions.types import ToolPermissionState
from ....context import FsContext
from ..execution import recursive_ls_tool


##


@pytest.mark.asyncs('asyncio')
async def test_recursive_ls_tool():
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

    tool_invoker = NameSwitchedToolInvoker({
        check.not_none(rlt.name): rlt.invoker(),
    })

    with cxl.bind({
        FsContext: FsContext(
            root_dir=FsRoot(root_dir),
            tool_permission_decider=StaticToolPermissionDecider(ToolPermissionState.ALLOW),
        ),
    }):
        tool_exec_result = await execute_tool_use(
            tool_invoker,
            tool_exec_request,
        )

    print()
    print(tool_exec_result.c)
