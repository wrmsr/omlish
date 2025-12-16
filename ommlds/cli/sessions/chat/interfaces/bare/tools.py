import typing as ta

from ..... import minichain as mc
from ....rendering.types import ContentRendering
from .execution import ToolUseExecutor


##


class ArgsRenderingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
            renderer: ContentRendering,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._renderer = renderer

    async def execute_tool_use(
            self,
            use: 'mc.ToolUse',
            *ctx_items: ta.Any,
    ) -> 'mc.ToolUseResultMessage':
        await self._renderer.render_content(mc.JsonContent(dict(
            id=use.id,
            name=use.name,
            args=use.args,
        )))

        return await self._wrapped.execute_tool_use(use, *ctx_items)


class ResultRenderingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
            renderer: ContentRendering,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._renderer = renderer

    async def execute_tool_use(
            self,
            use: 'mc.ToolUse',
            *ctx_items: ta.Any,
    ) -> 'mc.ToolUseResultMessage':
        out = await self._wrapped.execute_tool_use(use, *ctx_items)

        await self._renderer.render_content(out.tur.c)

        return out
