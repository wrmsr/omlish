import typing as ta

from omlish import check
from omlish import dataclasses as dc

from ....tools.fns import ToolFn
from ....tools.types import ToolSpec
from ...tools.execution.context import ToolContext
from .executors import ToolExecutor
from .executors import ToolFnToolExecutor


##


@dc.dataclass(frozen=True)
class ToolCatalogEntry:
    spec: ToolSpec
    target: ToolFn | ToolExecutor


ToolCatalogEntries = ta.NewType('ToolCatalogEntries', ta.Sequence[ToolCatalogEntry])


class ToolCatalog(ToolExecutor):
    def __init__(
            self,
            entries: ToolCatalogEntries,
    ) -> None:
        super().__init__()

        self._entries = [check.isinstance(e, ToolCatalogEntry) for e in entries]

        by_name: dict[str, ToolCatalogEntry] = {}
        for e in self._entries:
            n = check.non_empty_str(e.spec.name)
            check.not_in(n, by_name)
            by_name[n] = e
        self._by_name = by_name

    @property
    def by_name(self) -> ta.Mapping[str, ToolCatalogEntry]:
        return self._by_name

    def execute_tool(
            self,
            ctx: ToolContext,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> str:
        e = self._by_name[name]

        x: ToolExecutor
        if isinstance(e.target, ToolExecutor):
            x = e.target
        elif isinstance(e.target, ToolFn):
            x = ToolFnToolExecutor(e.target)
        else:
            raise TypeError(e.target)

        return x.execute_tool(
            ctx,
            name,
            args,
        )
