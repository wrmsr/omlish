"""
TODO:
 - join
 - subquery
"""
import typing as ta

from ... import dataclasses as dc
from ... import lang
from .base import Node
from .idents import Ident
from .names import CanName
from .names import Name
from .names import NameBuilder


##


class Relation(Node, lang.Abstract):
    pass


class Table(Relation, lang.Final):
    n: Name
    a: Ident | None = dc.xfield(None, repr_fn=dc.opt_repr)


CanTable: ta.TypeAlias = Table | CanName
CanRelation: ta.TypeAlias = Relation | CanTable


class RelationBuilder(NameBuilder):
    def table(self, n: CanTable) -> Table:
        if isinstance(n, Table):
            return n
        else:
            return Table(self.name(n))

    def relation(self, o: CanRelation) -> Relation:
        if isinstance(o, Relation):
            return o
        else:
            return self.table(o)
