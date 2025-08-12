from omlish import lang

from ...tools.execution.context import ToolContext
from ...tools.execution.executors import ToolExecutor
from ..messages import ToolExecRequest
from ..messages import ToolExecResultMessage


##


@lang.maysync
async def m_execute_tool_request(
        ctx: ToolContext,
        tex: ToolExecutor,
        ter: ToolExecRequest,
) -> ToolExecResultMessage:
    result_str = await tex.m_execute_tool(
        ctx,
        ter.name,
        ter.args,
    ).m()

    return ToolExecResultMessage(
        id=ter.id,
        name=ter.name,
        c=result_str,
    )
