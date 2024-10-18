import enum
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder


##


class MultiKind(enum.Enum):
    AND = enum.auto()
    OR = enum.auto()


class Multi(Expr, lang.Final):
    k: MultiKind
    es: ta.Sequence[Expr] = dc.xfield(coerce=tuple, validate=lambda es: len(es) > 1)


class MultiBuilder(ExprBuilder):
    def multi(self, k: MultiKind, *es: CanExpr) -> Expr:
        check.not_empty(es)
        if len(es) == 1:
            return self.expr(es[0])
        else:
            return Multi(k, [self.expr(e) for e in es])

    def and_(self, *es: CanExpr) -> Expr:
        return self.multi(MultiKind.AND, *es)

    def or_(self, *es: CanExpr) -> Expr:
        return self.multi(MultiKind.OR, *es)
