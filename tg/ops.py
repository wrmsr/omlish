import typing as ta

from omlish import collections as col

from tinygrad import ops as tgops
from nn import ops as ops
from .lazy import Lazy
from .lazy import LazyBuffer
from .lazy import LazyOp


_OP_CONVERTERS: ta.Mapping[_ops.Op, ta.Callable[[LazyOp], Op]] = {
    **{o: (lambda ot: lambda op: ot(convert_from_lazy(op.srcs[0])))(ot) for o, ot in [
        (tgops.UnaryOps.NOOP, ops.Nop),
        (tgops.UnaryOps.EXP2, ops.Exp2),
        (tgops.UnaryOps.LOG2, ops.Log2),
        (tgops.UnaryOps.SIN, ops.Sin),
        (tgops.UnaryOps.RECIP, ops.Recip),
    ]},
    _ops.UnaryOp.CAST: lambda op: Cast(convert_from_lazy(op.srcs[0]), check.isinstance(op.arg, Dtype)),

    **{o: (lambda ot: lambda op: ot(convert_from_lazy(op.srcs[0]), convert_from_lazy(op.srcs[1])))(ot) for o, ot in [
        (tgops.BinaryOps.ADD, ops.Add),
        (tgops.BinaryOps.SUB, ops.Sub),
        (tgops.BinaryOps.MUL, ops.Mul),
        (tgops.BinaryOps.DIV, ops.Div),
        (tgops.BinaryOps.CMPEQ, ops.CmpEq),
        (tgops.BinaryOps.MAX, ops.Maximum),
        (tgops.BinaryOps.MOD, ops.Mod),
    ]},

    **{o: (lambda ot: lambda op: ot(convert_from_lazy(op.srcs[0]), check.isinstance(op.arg, Shape)))(ot) for o, ot in [
        (tgops.ReduceOps.SUM, ops.Sum),
        (tgops.ReduceOps.MAX, ops.Max),
    ]},

    _ops.MovementOp.RESHAPE: lambda op: Reshape(convert_from_lazy(op.srcs[0]), check.isinstance(op.arg, Shape)),
    _ops.MovementOp.PERMUTE: lambda op: Permute(convert_from_lazy(op.srcs[0]), col.seq_of(check.of_isinstance(int))(op.arg)),  # noqa
    _ops.MovementOp.EXPAND: lambda op: Expand(convert_from_lazy(op.srcs[0]), check.isinstance(op.arg, Shape)),
}


def convert_from_lazy_op(op: LazyOp) -> Op:
    # _ops.MovementOp.PAD
    # _ops.MovementOp.SHRINK
    # _ops.MovementOp.STRIDE
    #
    # _ops.FusedOp.MUL_ACC
    #
    # _ops.LoadOp.EMPTY
    # _ops.LoadOp.RAND
    # _ops.LoadOp.CONST
    # _ops.LoadOp.FROM
    # _ops.LoadOp.CONTIGUOUS
    # _ops.LoadOp.CUSTOM

    return _OP_CONVERTERS[op.op](op)


def convert_from_lazy(laz: Lazy) -> Lazy:
    if isinstance(laz, LazyOp):
        return convert_from_lazy_op(laz)
    if isinstance(laz, LazyBuffer):
        return Buffer(laz)
    raise TypeError(laz)
