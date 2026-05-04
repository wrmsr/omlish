import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...tools.execution.catalog import ToolCatalogEntry
from ...tools.execution.context import ToolContext
from ...tools.types import ToolUse
from ..types import ToolUseResult
from .context import ToolContextProvider
from .invokers import ToolInvoker


##


@ta.final
@dc.dataclass(frozen=True)
class ToolUseExecution(lang.Final):
    use: ToolUse

    catalog_entry: ToolCatalogEntry | None = None

    ctx_items: ta.Sequence[ta.Any] = ()


class ToolUseExecutor(lang.Abstract):
    @abc.abstractmethod
    def execute_tool_use(self, tue: ToolUseExecution) -> ta.Awaitable[ToolUseResult]:
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

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResult:
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


##


async def execute_tool_use(
        ctx: ToolContext,
        tei: ToolInvoker,
        ter: ToolUse,
) -> ToolUseResult:
    result_str = await tei.invoke_tool(
        ctx,
        ter.name,
        ter.args,
    )

    return ToolUseResult(
        id=ter.id,
        name=ter.name,
        c=result_str,
    )
