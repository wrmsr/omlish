import operator
import typing as ta

from omlish import dispatch
from omlish.sql.queries import Binary
from omlish.sql.queries import BinaryOp
from omlish.sql.queries import BinaryOps
from omlish.sql.queries import Expr
from omlish.sql.queries import Literal
from omlish.sql.queries import Unary
from omlish.sql.queries import Relation
from omlish.sql.queries import UnaryOp
from omlish.sql.queries import UnaryOps


##


class ExprEvaluator:
    def eval(self, expr: Expr) -> ta.Any:
        return self._eval(expr)

    @dispatch.method
    def _eval(self, expr: Expr) -> ta.Any:
        raise TypeError(expr)

    _BINARY_OP_MAP: ta.Mapping[BinaryOp, ta.Callable] = {
        BinaryOps.EQ: operator.eq,
        BinaryOps.NE: operator.ne,
        BinaryOps.LT: operator.lt,
        BinaryOps.LE: operator.le,
        BinaryOps.GT: operator.gt,
        BinaryOps.GE: operator.ge,

        BinaryOps.ADD: operator.add,
        BinaryOps.SUB: operator.sub,
        BinaryOps.MUL: operator.mul,
        BinaryOps.DIV: operator.truediv,
        BinaryOps.MOD: operator.mod,

        BinaryOps.CONCAT: operator.add,
    }

    @_eval.register
    def _eval_binary(self, expr: Binary) -> ta.Any:
        op = self._BINARY_OP_MAP[expr.op]
        l = self.eval(expr.l)
        r = self.eval(expr.r)
        return op(l, r)

    @_eval.register
    def _eval_literal(self, expr: Literal) -> ta.Any:
        return expr.v

    _UNARY_OP_MAP: ta.Mapping[UnaryOp, ta.Any] = {
        UnaryOps.NOT: operator.not_,
        UnaryOps.IS_NULL: lambda v: v is None,
        UnaryOps.IS_NOT_NULL: lambda v: v is not None,

        UnaryOps.POS: operator.pos,
        UnaryOps.NEG: operator.neg,
    }

    @_eval.register
    def _eval_unary(self, expr: Unary) -> ta.Any:
        op = self._UNARY_OP_MAP[expr.op]
        v = self.eval(expr.v)
        return op(v)


##


class RelationEvaluator:
    def eval(self, rel: Relation) -> list[tuple]:
        return self._eval(rel)

    @dispatch.method
    def _eval(self, rel: Relation) -> list[tuple]:
        raise TypeError(rel)
