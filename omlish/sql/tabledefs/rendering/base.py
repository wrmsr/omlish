import abc

from .... import lang
from ..tabledefs import TableDef


##


class StatementRenderer(lang.Abstract):
    @abc.abstractmethod
    def render_create_statements(
            self,
            tbl: TableDef,
            *,
            if_not_exists: bool = False,
    ) -> list[str]:
        raise NotImplementedError
