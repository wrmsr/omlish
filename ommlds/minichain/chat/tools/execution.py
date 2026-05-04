from ...tools.execution.context import ToolContext
from ...tools.execution.invokers import ToolInvoker
from ...tools.types import ToolUse
from ...tools.types import ToolUseResult
from ..messages import ToolUseResultMessage


##


async def execute_tool_use(
        ctx: ToolContext,
        tei: ToolInvoker,
        ter: ToolUse,
) -> ToolUseResultMessage:
    result_str = await tei.invoke_tool(
        ctx,
        ter.name,
        ter.args,
    )

    return ToolUseResultMessage(ToolUseResult(
        id=ter.id,
        name=ter.name,
        c=result_str,
    ))
