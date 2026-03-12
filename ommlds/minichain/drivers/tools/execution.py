import abc
import typing as ta

from omlish import check
from omlish import lang

from ...chat.messages import ToolUseResultMessage
from ...chat.tools.execution import execute_tool_use
from ...tools.execution.catalog import ToolCatalog
from ...tools.execution.context import ToolContext
from ...tools.types import ToolUse
from .confirmation import ToolExecutionConfirmation


##


class ToolContextProvider(lang.Func0[ta.Sequence[ta.Any]]):
    pass


ToolContextProviders = ta.NewType('ToolContextProviders', ta.Sequence[ToolContextProvider])


##


class ToolUseExecutor(lang.Abstract):
    @abc.abstractmethod
    def execute_tool_use(
            self,
            use: ToolUse,
            *ctx_items: ta.Any,
    ) -> ta.Awaitable[ToolUseResultMessage]:
        raise NotImplementedError


class ToolUseExecutorImpl(ToolUseExecutor):
    def __init__(
            self,
            *,
            catalog: ToolCatalog,
            ctx_provider: ToolContextProvider,
            confirmation: ToolExecutionConfirmation,
    ) -> None:
        super().__init__()

        self._catalog = catalog
        self._ctx_provider = ctx_provider
        self._confirmation = confirmation

    async def execute_tool_use(
            self,
            use: ToolUse,
            *ctx_items: ta.Any,
    ) -> ToolUseResultMessage:
        tce = self._catalog.by_name[check.non_empty_str(use.name)]

        await self._confirmation.confirm_tool_execution_or_raise(use, tce)

        return await execute_tool_use(
            ToolContext(
                use,
                *self._ctx_provider(),
                *ctx_items,
            ),
            tce.executor(),
            use,
        )
