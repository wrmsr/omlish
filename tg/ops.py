import typing as ta

from omlish import check
from omlish import collections as col

from tinygrad import ops as tgops
from tinygrad.lazy import LazyBuffer as TgLazyBuffer
from tinygrad.lazy import LazyOp as TgLazyOp

from nn import ops
from nn.buffers import Buffer
from nn.dims import Shape
from nn.dims import Stride
from nn.dtypes import Dtype
from nn.lazy import Lazy
from nn.tensor import Tensor


TgLazy = ta.Union[TgLazyOp, TgLazyBuffer]


_TG_OP_CONVERTERS: ta.Mapping[tgops.Op, ta.Callable[[TgLazyOp], ops.Op]] = {
    **{o: (lambda ot: lambda op: ot(convert_from_tg_lazy(op.srcs[0])))(ot) for o, ot in [
        (tgops.UnaryOps.NOOP, ops.Nop),
        (tgops.UnaryOps.EXP2, ops.Exp2),
        (tgops.UnaryOps.LOG2, ops.Log2),
        (tgops.UnaryOps.SIN, ops.Sin),
        (tgops.UnaryOps.RECIP, ops.Recip),
    ]},
    tgops.UnaryOps.CAST: lambda op: ops.Cast(convert_from_tg_lazy(op.srcs[0]), check.isinstance(op.arg, Dtype)),

    **{o: (lambda ot: lambda op: ot(convert_from_tg_lazy(op.srcs[0]), convert_from_tg_lazy(op.srcs[1])))(ot) for o, ot in [  # noqa
        (tgops.BinaryOps.ADD, ops.Add),
        (tgops.BinaryOps.SUB, ops.Sub),
        (tgops.BinaryOps.MUL, ops.Mul),
        (tgops.BinaryOps.DIV, ops.Div),
        (tgops.BinaryOps.CMPEQ, ops.CmpEq),
        (tgops.BinaryOps.MAX, ops.Maximum),
        (tgops.BinaryOps.MOD, ops.Mod),
    ]},

    **{o: (lambda ot: lambda op: ot(convert_from_tg_lazy(op.srcs[0]), check.isinstance(op.arg, Shape)))(ot) for o, ot in [  # noqa
        (tgops.ReduceOps.SUM, ops.Sum),
        (tgops.ReduceOps.MAX, ops.Max),
    ]},

    tgops.MovementOps.RESHAPE: lambda op: ops.Reshape(convert_from_tg_lazy(op.srcs[0]), check.isinstance(op.arg, Shape)),  # noqa
    tgops.MovementOps.PERMUTE: lambda op: ops.Permute(convert_from_tg_lazy(op.srcs[0]), col.seq_of(check.of_isinstance(int))(op.arg)),  # noqa
    tgops.MovementOps.EXPAND: lambda op: ops.Expand(convert_from_tg_lazy(op.srcs[0]), check.isinstance(op.arg, Shape)),
}


def convert_from_tg_lazy_op(op: TgLazyOp) -> ops.Op:
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

    return _TG_OP_CONVERTERS[op.op](op)


def convert_from_tg_lazy(laz: TgLazy) -> Lazy:
    if isinstance(laz, TgLazyOp):
        return convert_from_tg_lazy_op(laz)
    if isinstance(laz, TgLazyBuffer):
        return Buffer(laz)
    raise TypeError(laz)
