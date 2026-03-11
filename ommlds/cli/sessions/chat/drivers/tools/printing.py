import typing as ta

from ...... import minichain as mc
from .....interfaces.bare.printing.types import ContentPrinting
from ...drivers.tools.execution import ToolUseExecutor


##


class ArgsPrintingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
            printer: ContentPrinting,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._printer = printer

    async def execute_tool_use(
            self,
            use: 'mc.ToolUse',
            *ctx_items: ta.Any,
    ) -> 'mc.ToolUseResultMessage':
        await self._printer.print_content(mc.JsonContent(dict(
            id=use.id,
            name=use.name,
            args=use.args,
        )))

        return await self._wrapped.execute_tool_use(use, *ctx_items)


class ResultPrintingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
            printer: ContentPrinting,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._printer = printer

    async def execute_tool_use(
            self,
            use: 'mc.ToolUse',
            *ctx_items: ta.Any,
    ) -> 'mc.ToolUseResultMessage':
        out = await self._wrapped.execute_tool_use(use, *ctx_items)

        await self._printer.print_content(out.tur.c)

        return out
