"""
TODO:
 - join
 - subquery
"""
import enum
import typing as ta

from ... import dataclasses as dc
from ... import lang
from .base import Node
from .exprs import CanExpr
from .exprs import Expr
from .idents import Ident
from .multi import MultiBuilder
from .names import CanName
from .names import Name


##


class Relation(Node, lang.Abstract):
    pass


#


class Table(Relation, lang.Final):
    n: Name
    a: Ident | None = dc.xfield(None, repr_fn=dc.opt_repr)


#


class JoinKind(enum.Enum):
    DEFAULT = enum.auto()
    INNER = enum.auto()
    LEFT = enum.auto()
    LEFT_OUTER = enum.auto()
    RIGHT = enum.auto()
    RIGHT_OUTER = enum.auto()
    FULL = enum.auto()
    FULL_OUTER = enum.auto()
    CROSS = enum.auto()
    NATURAL = enum.auto()


class Join(Relation, lang.Final):
    k: JoinKind
    l: Relation
    r: Relation

    c: Expr | None = None


##


CanTable: ta.TypeAlias = Table | CanName
CanRelation: ta.TypeAlias = Relation | CanTable


class RelationBuilder(MultiBuilder):
    def table(self, n: CanTable) -> Table:
        if isinstance(n, Table):
            return n
        else:
            return Table(self.name(n))

    #

    def join(
            self,
            k: JoinKind,
            l: CanRelation,
            r: CanRelation,
            *cs: CanExpr,
    ) -> Join:
        return Join(
            k,
            self.relation(l),
            self.relation(r),
            self.or_(*cs) if cs else None,
        )

    def default_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.DEFAULT, l, r, *cs)

    def inner_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.INNER, l, r, *cs)

    def left_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.LEFT, l, r, *cs)

    def left_outer_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.LEFT_OUTER, l, r, *cs)

    def right_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.RIGHT, l, r, *cs)

    def right_outer_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.RIGHT_OUTER, l, r, *cs)

    def full_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.FULL, l, r, *cs)

    def full_outer_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.FULL_OUTER, l, r, *cs)

    def cross_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.CROSS, l, r, *cs)

    def natural_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinKind.NATURAL, l, r, *cs)

    #

    def relation(self, o: CanRelation) -> Relation:
        if isinstance(o, Relation):
            return o
        else:
            return self.table(o)
