import abc

from .... import dataclasses as dc
from .... import lang
from ..tabledefs import TableDef


##


class StatementRenderer(lang.Abstract):
    @dc.dataclass(frozen=True, kw_only=True)
    class CreateOptions:
        drop_if_exists: bool = False
        if_not_exists: bool = False

    @abc.abstractmethod
    def render_create_statements(
            self,
            tbl: TableDef,
            opts: CreateOptions | None = None,
    ) -> list[str]:
        raise NotImplementedError
