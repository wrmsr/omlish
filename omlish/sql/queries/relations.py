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


class JoinType(enum.Enum):
    DEFAULT = ''
    INNER = 'inner'
    LEFT = 'left'
    LEFT_OUTER = 'left outer'
    RIGHT = 'right'
    RIGHT_OUTER = 'right outer'
    FULL = 'full'
    FULL_OUTER = 'full outer'
    CROSS = 'cross'
    NATURAL = 'natural'


class Join(Relation, lang.Final):
    t: JoinType
    l: Relation
    r: Relation

    c: Expr | None = None


##


CanTable: ta.TypeAlias = Table | CanName
CanJoinType: ta.TypeAlias = JoinType | str
CanRelation: ta.TypeAlias = Relation | CanTable


class RelationBuilder(MultiBuilder):
    def table(self, n: CanTable) -> Table:
        if isinstance(n, Table):
            return n
        else:
            return Table(self.name(n))

    #

    def join_type(self, t: CanJoinType) -> JoinType:
        if isinstance(t, JoinType):
            return t
        else:
            return JoinType(t)

    def join(
            self,
            t: CanJoinType,
            l: CanRelation,
            r: CanRelation,
            *cs: CanExpr,
    ) -> Join:
        return Join(
            self.join_type(t),
            self.relation(l),
            self.relation(r),
            self.or_(*cs) if cs else None,
        )

    def default_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.DEFAULT, l, r, *cs)

    def inner_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.INNER, l, r, *cs)

    def left_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.LEFT, l, r, *cs)

    def left_outer_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.LEFT_OUTER, l, r, *cs)

    def right_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.RIGHT, l, r, *cs)

    def right_outer_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.RIGHT_OUTER, l, r, *cs)

    def full_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.FULL, l, r, *cs)

    def full_outer_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.FULL_OUTER, l, r, *cs)

    def cross_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.CROSS, l, r, *cs)

    def natural_join(self, l: CanRelation, r: CanRelation, *cs: CanExpr) -> Join:
        return self.join(JoinType.NATURAL, l, r, *cs)

    #

    def relation(self, o: CanRelation) -> Relation:
        if isinstance(o, Relation):
            return o
        else:
            return self.table(o)
