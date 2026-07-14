import abc
import typing as ta

from omcore import check
from omcore import collections as col
from omcore import contextual as cxl
from omcore import dataclasses as dc
from omcore import lang

from ...tools.execution.catalog import ToolCatalogEntry
from ...tools.fns import ToolFn
from ...tools.types import ToolUse
from ..types import ToolUseResult
from .context import ToolContextProvider
from .context import ToolContextProviders
from .invokers import ToolInvoker


##


@ta.final
@dc.dataclass(frozen=True)
class ToolUseExecution(lang.Final):
    use: ToolUse

    catalog_entry: ToolCatalogEntry | None = None


class ToolUseExecutor(lang.Abstract):
    @abc.abstractmethod
    def execute_tool_use(self, tue: ToolUseExecution) -> ta.Awaitable[ToolUseResult]:
        raise NotImplementedError


##


class ToolUseExecutorImpl(ToolUseExecutor):
    def __init__(
            self,
            *,
            ctx_providers: ToolContextProviders,
    ) -> None:
        super().__init__()

        self._ctx_providers = ctx_providers

        self._ctx_providers_by_ty: ta.Mapping[type, ToolContextProvider] = col.make_map(
            ((cp.ty, cp) for cp in self._ctx_providers),
            strict=True,
        )

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResult:
        cbs: dict[type, ta.Any] = {}

        tce = check.not_none(tue.catalog_entry)
        if isinstance(tfn := tce.target, ToolFn):
            cbs.update({
                ty: self._ctx_providers_by_ty[ty].fn()
                for ty in tfn.context or []
            })

        with cxl.bind({
            ToolUseExecution: tue,
            ToolUse: tue.use,
            **cbs,
        }):
            return await execute_tool_use(
                check.not_none(tue.catalog_entry).invoker(),
                tue.use,
            )


##


async def execute_tool_use(
        tei: ToolInvoker,
        ter: ToolUse,
) -> ToolUseResult:
    result_str = await tei.invoke_tool(
        ter.name,
        ter.args,
    )

    return ToolUseResult(
        id=ter.id,
        name=ter.name,
        c=result_str,
    )
