import typing as ta

from ...content.content import Content
from .context import ToolContext
from .errors import ToolExecutionError
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
