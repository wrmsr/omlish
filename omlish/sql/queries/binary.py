from ... import check
from ... import dataclasses as dc
from ... import lang
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .ops import OpKind


##


class BinaryOp(dc.Frozen, lang.Final, eq=False):
    name: str
    kind: OpKind


class BinaryOps(lang.Namespace):
    ADD = BinaryOp('add', OpKind.ARITH)
    SUB = BinaryOp('sub', OpKind.ARITH)

    EQ = BinaryOp('eq', OpKind.CMP)
    NE = BinaryOp('ne', OpKind.CMP)


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
