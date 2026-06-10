import abc

from ... import lang
from ..api.queriers import Querier
from ..tabledefs.tabledefs import TableDef
from .reflected import ReflectedTable


##


class Inspector(lang.Abstract):
    """
    A backend's live-db introspection facet. `reflect_table` does IO (it reads the catalog via a Querier) and is
    fail-open; `lift_table` is a pure, lossy conversion of the reflected snapshot into a tabledef that can be diffed
    against the in-code definition.
    """

    @abc.abstractmethod
    def reflect_table(self, querier: Querier, name: str) -> ReflectedTable | None:
        raise NotImplementedError

    @abc.abstractmethod
    def lift_table(self, reflected: ReflectedTable) -> TableDef:
        raise NotImplementedError
