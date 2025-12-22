import typing as ta

from omlish import check

from ...content.types import Content
from .context import ToolContext
from .errors import ToolExecutionError
from .executors import ToolExecutor


##


class ErrorHandlingToolExecutor(ToolExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolExecutor,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped

    async def execute_tool(
            self,
            ctx: ToolContext,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> Content:
        try:
            return await self._wrapped.execute_tool(ctx, name, args)

        except ToolExecutionError as txe:
            return check.isinstance(txe.content, str)  # FIXME
