from ....tools.fns import ToolFn
from ....tools.fns import execute_tool_fn
from ...messages import ToolExecRequest
from ...messages import ToolExecResultMessage
from .context import ToolContext
from .context import bind_tool_context


##


def execute_tool_request(
        ctx: ToolContext,
        te: ToolFn,
        ter: ToolExecRequest,
) -> ToolExecResultMessage:
    with bind_tool_context(ctx):
        result_str = execute_tool_fn(
            te,
            ter.args,
        )

        return ToolExecResultMessage(
            ter.id,
            ter.name,
            result_str,
        )
