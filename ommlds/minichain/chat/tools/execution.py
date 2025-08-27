from ...tools.execution.context import ToolContext
from ...tools.execution.executors import ToolExecutor
from ..messages import ToolExecRequest
from ..messages import ToolExecResultMessage


##


async def execute_tool_request(
        ctx: ToolContext,
        tex: ToolExecutor,
        ter: ToolExecRequest,
) -> ToolExecResultMessage:
    result_str = await tex.execute_tool(
        ctx,
        ter.name,
        ter.args,
    )

    return ToolExecResultMessage(
        id=ter.id,
        name=ter.name,
        c=result_str,
    )
