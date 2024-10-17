import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from .base import Node
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder


##


class MultiOp(Node, lang.Final):
    name: str


class MultiOps(lang.Namespace):
    AND = MultiOp('and')
    OR = MultiOp('or')


class Multi(Expr, lang.Final):
    op: MultiOp
    es: ta.Sequence[Expr] = dc.xfield(coerce=tuple)


class MultiBuilder(ExprBuilder):
    def multi(self, op: MultiOp, *es: CanExpr) -> Expr:
        check.not_empty(es)
        if len(es) == 1:
            return self.expr(es[0])
        else:
            return Multi(op, [self.expr(e) for e in es])

    def and_(self, *es: CanExpr) -> Expr:
        return self.multi(MultiOps.AND, *es)

    def or_(self, *es: CanExpr) -> Expr:
        return self.multi(MultiOps.OR, *es)
