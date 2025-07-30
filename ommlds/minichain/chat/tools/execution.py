from ...tools.execution.context import ToolContext
from ...tools.execution.execution import execute_tool_fn
from ...tools.execution.types import ToolFn
from ..messages import ToolExecRequest
from ..messages import ToolExecResultMessage


##


def execute_tool_request(
        ctx: ToolContext,
        te: ToolFn,
        ter: ToolExecRequest,
) -> ToolExecResultMessage:
    result_str = execute_tool_fn(
        ctx,
        te,
        ter.args,
    )

    return ToolExecResultMessage(
        ter.id,
        ter.name,
        result_str,
    )
