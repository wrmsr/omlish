import operator as op
import typing as ta

from .. import nodes as no
from ... import dispatch
from ... import lang
from .contexts import EvalContext


BIN_OP_MAP: ta.Mapping[no.BinOp, ta.Callable[[ta.Any, ta.Any], ta.Any]] = {
    no.BinOps.ADD: op.add,
    no.BinOps.SUB: op.sub,
    no.BinOps.MUL: op.mul,
    no.BinOps.DIV: op.truediv,
    no.BinOps.MOD: op.mod,

    no.BinOps.BIT_AND: op.and_,
    no.BinOps.BIT_OR: op.or_,
    no.BinOps.BIT_XOR: op.xor,

    no.BinOps.LSH: op.lshift,
    no.BinOps.RSH: op.rshift,

    no.BinOps.FLOOR_DIV: op.floordiv,
    no.BinOps.POW: op.pow,
    no.BinOps.MAT_MUL: op.matmul,
}


CMP_OP_MAP: ta.Mapping[no.CmpOp, ta.Callable[[ta.Any, ta.Any], ta.Any]] = {
    no.CmpOps.EQ: op.eq,
    no.CmpOps.NE: op.ne,
    no.CmpOps.GT: op.gt,
    no.CmpOps.GE: op.ge,
    no.CmpOps.LT: op.lt,
    no.CmpOps.LE: op.le,

    no.CmpOps.IS: op.is_,
    no.CmpOps.IS_NOT: op.is_not,

    no.CmpOps.IN: lambda l, r: l in r,
    no.CmpOps.NOT_IN: lambda l, r: l not in r,
}


UNARY_OP_MAP: ta.Mapping[no.UnaryOp, ta.Callable[[ta.Any], ta.Any]] = {
    no.UnaryOps.PLUS: lambda v: +v,
    no.UnaryOps.MINUS: lambda v: -v,
    no.UnaryOps.INVERT: lambda v: ~v,

    no.UnaryOps.NOT: lambda v: not v,
}


class NOTHING(lang.Marker):
    pass


class Evaluator(dispatch.Class):
    __call__ = dispatch.property()

    def __call__(self, node: no.Node, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise TypeError(node)

    def __call__(self, node: no.BinExpr, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        left, ctx = self(node.left, ctx)
        right, ctx = self(node.right, ctx)
        fn = BIN_OP_MAP[node.op]
        ret = fn(left, right)
        return ret, ctx

    def __call__(self, node: no.BoolExpr, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.Break, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.Call, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.CmpExpr, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        left, ctx = self(node.left, ctx)
        right, ctx = self(node.right, ctx)
        fn = CMP_OP_MAP[node.op]
        ret = fn(left, right)
        return ret, ctx

    def __call__(self, node: no.Const, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        return node.value, ctx

    def __call__(self, node: no.Continue, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.ExprStmt, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        _, ctx = self(node.expr)
        return NOTHING, ctx

    def __call__(self, node: no.ForIter, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.GetAttr, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.GetItem, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.GetVar, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        return ctx.get_var(node.name.s), ctx

    def __call__(self, node: no.If, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.Pass, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        return NOTHING, ctx

    def __call__(self, node: no.Raise, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.Return, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.SetAttr, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.SetItem, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        raise NotImplementedError

    def __call__(self, node: no.SetVar, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        value, ctx = self(node.value)
        ctx = ctx.set_var(node.name.s, value, node)
        return NOTHING, ctx

    def __call__(self, node: no.UnaryExpr, ctx: EvalContext) -> ta.Tuple[ta.Any, EvalContext]:  # noqa
        value, ctx = self(node.left, ctx)
        fn = UNARY_OP_MAP[node.op]
        ret = fn(value)
        return ret, ctx
