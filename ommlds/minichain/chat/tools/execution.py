from ...tools.execution.context import ToolContext
from ...tools.execution.executors import ToolExecutor
from ...tools.types import ToolUseResult
from ..messages import ToolUse
from ..messages import ToolUseResultMessage


##


async def execute_tool_use(
        ctx: ToolContext,
        tex: ToolExecutor,
        ter: ToolUse,
) -> ToolUseResultMessage:
    result_str = await tex.execute_tool(
        ctx,
        ter.name,
        ter.args,
    )

    return ToolUseResultMessage(ToolUseResult(
        id=ter.id,
        name=ter.name,
        c=result_str,
    ))
