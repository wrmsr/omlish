import typing as ta

from omlish import check

from ...chat.messages import ToolUseResultMessage
from ...tools.execution.errors import ToolExecutionError
from ...tools.types import ToolUse
from ...tools.types import ToolUseResult
from .execution import ToolUseExecutor


##


class ErrorHandlingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped

    async def execute_tool_use(
            self,
            use: ToolUse,
            *ctx_items: ta.Any,
    ) -> ToolUseResultMessage:
        try:
            return await self._wrapped.execute_tool_use(use, *ctx_items)

        except ToolExecutionError as txe:  # noqa
            s = check.non_empty_str(check.isinstance(txe.content, str))

            return ToolUseResultMessage(
                ToolUseResult(
                    id=use.id,
                    name=use.name,
                    c=s,
                ),
            )
