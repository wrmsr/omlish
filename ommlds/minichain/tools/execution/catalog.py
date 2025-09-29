import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...content.types import Content
from ..fns import ToolFn
from ..types import ToolSpec
from .context import ToolContext
from .executors import ToolExecutor
from .executors import ToolFnToolExecutor


##


@dc.dataclass(frozen=True, eq=False)
class ToolCatalogEntry(lang.Final):
    spec: ToolSpec
    target: ToolFn | ToolExecutor

    _: dc.KW_ONLY

    name_override: str | None = dc.xfield(default=None, repr_fn=dc.opt_repr)

    @property
    def name(self) -> str:
        return check.non_empty_str(self.name_override if self.name_override is not None else self.spec.name)

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)

    @lang.cached_function
    def executor(self) -> ToolExecutor:
        if isinstance(self.target, ToolFn):
            return ToolFnToolExecutor(self.target)
        elif isinstance(self.target, ToolExecutor):
            return self.target
        else:
            raise TypeError(self.target)


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
            n = e.name
            check.not_in(n, by_name)
            by_name[n] = e
        self._by_name = by_name

    @property
    def by_name(self) -> ta.Mapping[str, ToolCatalogEntry]:
        return self._by_name

    async def execute_tool(
            self,
            ctx: ToolContext,
            name: str,
            args: ta.Mapping[str, ta.Any],
    ) -> Content:
        e = self._by_name[name]

        return await e.executor().execute_tool(
            ctx,
            name,
            args,
        )
