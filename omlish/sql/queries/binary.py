"""
TODO:
 - in_
 - like
  - no this is a dedicated node, escape / negation in grammar
"""
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
    EQ = BinaryOp('eq', OpKind.CMP)
    NE = BinaryOp('ne', OpKind.CMP)
    LT = BinaryOp('lt', OpKind.CMP)
    LE = BinaryOp('le', OpKind.CMP)
    GT = BinaryOp('gt', OpKind.CMP)
    GE = BinaryOp('ge', OpKind.CMP)

    ADD = BinaryOp('add', OpKind.ARITH)
    SUB = BinaryOp('sub', OpKind.ARITH)
    MUL = BinaryOp('mul', OpKind.ARITH)
    DIV = BinaryOp('div', OpKind.ARITH)
    MOD = BinaryOp('mod', OpKind.ARITH)

    CONCAT = BinaryOp('concat', OpKind.STR)


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

    #

    def eq(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.EQ, *es)

    def ne(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.NE, *es)

    def lt(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.LT, *es)

    def le(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.LE, *es)

    def gt(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.GT, *es)

    def ge(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.GE, *es)

    #

    def add(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.ADD, *es)

    def sub(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.SUB, *es)

    def mul(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.MUL, *es)

    def div(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.DIV, *es)

    def mod(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.MOD, *es)

    #

    def concat(self, *es: CanExpr) -> Expr:
        return self.binary(BinaryOps.CONCAT, *es)
