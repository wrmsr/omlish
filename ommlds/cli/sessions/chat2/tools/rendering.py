import typing as ta

from ..... import minichain as mc
from .execution import ToolUseExecutor


##


class ResultRenderingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped

    async def execute_tool_use(
            self,
            use: 'mc.ToolUse',
            *ctx_items: ta.Any,
    ) -> 'mc.ToolUseResultMessage':
        out = await self._wrapped.execute_tool_use(use, *ctx_items)

        return out
