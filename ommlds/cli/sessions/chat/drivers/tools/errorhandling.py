import typing as ta

from omlish import check

from ...... import minichain as mc
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
            use: 'mc.ToolUse',
            *ctx_items: ta.Any,
    ) -> 'mc.ToolUseResultMessage':
        try:
            return await self._wrapped.execute_tool_use(use, *ctx_items)

        except mc.ToolExecutionError as txe:  # noqa
            s = check.non_empty_str(check.isinstance(txe.content, str))

            return mc.ToolUseResultMessage(
                mc.ToolUseResult(
                    id=use.id,
                    name=use.name,
                    c=s,
                ),
            )
