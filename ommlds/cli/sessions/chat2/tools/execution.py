import abc
import typing as ta

from omlish import check
from omlish import lang

from ..... import minichain as mc
from .confirmation import ToolExecutionConfirmation


##


class ToolUseExecutor(lang.Abstract):
    @abc.abstractmethod
    def execute_tool_use(
            self,
            use: mc.ToolUse,
            *ctx_items: ta.Any,
    ) -> ta.Awaitable[mc.ToolUseResultMessage]:
        raise NotImplementedError


class ToolUseExecutorImpl(ToolUseExecutor):
    def __init__(
            self,
            *,
            catalog: mc.ToolCatalog,
            confirmation: ToolExecutionConfirmation | None = None,
    ) -> None:
        super().__init__()

        self._catalog = catalog
        self._confirmation = confirmation

    async def execute_tool_use(
            self,
            use: mc.ToolUse,
            *ctx_items: ta.Any,
    ) -> mc.ToolUseResultMessage:
        tce = self._catalog.by_name[check.non_empty_str(use.name)]

        if self._confirmation is not None:
            await self._confirmation.confirm_tool_execution_or_raise(use, tce)

        return await mc.execute_tool_use(
            mc.ToolContext(
                use,
                *ctx_items,
            ),
            tce.executor(),
            use,
        )
