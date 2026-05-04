import typing as ta

from omlish import check

from ...content.content import Content
from ..types import ToolUseResult
from .context import ToolContext
from .errors import ToolExecutionError
from .execution import ToolUseExecution
from .execution import ToolUseExecutor
from .invokers import ToolInvoker


##


class ErrorHandlingToolInvoker(ToolInvoker):
    def __init__(
            self,
            *,
            wrapped: ToolInvoker,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped

    async def invoke_tool(
            self,
            ctx: ToolContext,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> Content:
        try:
            return await self._wrapped.invoke_tool(ctx, name, args)

        except ToolExecutionError as txe:
            return txe.content


##


class ErrorHandlingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResult:
        try:
            return await self._wrapped.execute_tool_use(tue)

        except ToolExecutionError as txe:  # noqa
            s = check.non_empty_str(check.isinstance(txe.content, str))

            return ToolUseResult(
                id=tue.use.id,
                name=tue.use.name,
                c=s,
            )
