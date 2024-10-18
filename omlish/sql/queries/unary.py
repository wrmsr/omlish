from ... import dataclasses as dc
from ... import lang
from .exprs import CanExpr
from .exprs import Expr
from .exprs import ExprBuilder
from .ops import OpKind


##


class UnaryOp(dc.Frozen, lang.Final, eq=False):
    name: str
    kind: OpKind


class UnaryOps(lang.Namespace):
    NOT = UnaryOp('not', OpKind.CMP)


class Unary(Expr, lang.Final):
    op: UnaryOp
    v: Expr


class UnaryBuilder(ExprBuilder):
    def unary(self, op: UnaryOp, v: CanExpr) -> Unary:
        return Unary(op, self.expr(v))

    def not_(self, v: CanExpr) -> Unary:
        return self.unary(UnaryOps.NOT, v)
