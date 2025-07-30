from ...messages import ToolExecRequest
from ...messages import ToolExecResultMessage
from .context import ToolContext
from .executors import ToolExecutor


##


def execute_tool_request(
        ctx: ToolContext,
        tex: ToolExecutor,
        ter: ToolExecRequest,
) -> ToolExecResultMessage:
    result_str = tex.execute_tool(
        ctx,
        ter.name,
        ter.args,
    )

    return ToolExecResultMessage(
        ter.id,
        ter.name,
        result_str,
    )
