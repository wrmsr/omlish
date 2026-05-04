import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import ToolUseResultMessage
from ...chat.tools.execution import execute_tool_use
from ...tools.execution.catalog import ToolCatalogEntry
from ...tools.execution.context import ToolContext
from ...tools.types import ToolUse


##


class ToolContextProvider(lang.Func0[ta.Sequence[ta.Any]]):
    pass


ToolContextProviders = ta.NewType('ToolContextProviders', ta.Sequence[ToolContextProvider])


##


@ta.final
@dc.dataclass(frozen=True)
class ToolUseExecution(lang.Final):
    use: ToolUse

    catalog_entry: ToolCatalogEntry | None = None

    ctx_items: ta.Sequence[ta.Any] = ()


class ToolUseExecutor(lang.Abstract):
    @abc.abstractmethod
    def execute_tool_use(self, tue: ToolUseExecution) -> ta.Awaitable[ToolUseResultMessage]:
        raise NotImplementedError


##


class ToolUseExecutorImpl(ToolUseExecutor):
    def __init__(
            self,
            *,
            ctx_provider: ToolContextProvider,
    ) -> None:
        super().__init__()

        self._ctx_provider = ctx_provider

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResultMessage:
        return await execute_tool_use(
            ToolContext(
                tue,
                tue.use,
                *self._ctx_provider(),
                *tue.ctx_items,
            ),
            check.not_none(tue.catalog_entry).invoker(),
            tue.use,
        )
