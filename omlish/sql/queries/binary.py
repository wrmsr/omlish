import enum

from ... import check
from ... import dataclasses as dc
from ... import lang
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder


##


class BinaryOpKind(enum.Enum):
    ARITH = enum.auto()
    BIT = enum.auto()
    CMP = enum.auto()


class BinaryOp(dc.Frozen, lang.Final, eq=False):
    name: str
    kind: BinaryOpKind


class BinaryOps(lang.Namespace):
    ADD = BinaryOp('add', BinaryOpKind.ARITH)
    SUB = BinaryOp('sub', BinaryOpKind.ARITH)

    EQ = BinaryOp('eq', BinaryOpKind.CMP)
    NE = BinaryOp('ne', BinaryOpKind.CMP)


class Binary(Expr, lang.Final):
    op: BinaryOp
    l: Expr
    r: Expr


class BinaryBuilder(ExprBuilder):
    def binary(self, op: BinaryOp, *es: CanExpr) -> Expr:
        check.not_empty(es)
        l = self.expr(es[0])
        for r in es[1:]:
            l = Binary(op, l, self.expr(r))
        return l

    def add(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.ADD, *es)

    def sub(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.SUB, *es)

    def eq(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.EQ, *es)

    def ne(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.NE, *es)
