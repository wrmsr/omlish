from omlish import check

from ...chat.messages import ToolUseResultMessage
from ...tools.execution.errors import ToolExecutionError
from ...tools.types import ToolUseResult
from .execution import ToolUseExecution
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

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResultMessage:
        try:
            return await self._wrapped.execute_tool_use(tue)

        except ToolExecutionError as txe:  # noqa
            s = check.non_empty_str(check.isinstance(txe.content, str))

            return ToolUseResultMessage(
                ToolUseResult(
                    id=tue.use.id,
                    name=tue.use.name,
                    c=s,
                ),
            )
