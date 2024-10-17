from ... import check
from ... import lang
from .base import Node
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder


##


class BinaryOp(Node, lang.Final):
    name: str


class BinaryOps(lang.Namespace):
    ADD = BinaryOp('add')
    SUB = BinaryOp('sub')

    EQ = BinaryOp('eq')
    NE = BinaryOp('ne')


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
