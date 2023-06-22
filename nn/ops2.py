"""
TODO:
 - identity eq? identity cols?
"""
import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .dims import Shape
from .dims import Stride
from .dtypes import Dtype


#


class Source(lang.Sealed, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Buffer(Source):
    obj: ta.Any  # FIXME: LazyBuffer


@dc.dataclass(frozen=True)
class Op(Source, lang.Abstract):
    @property
    @abc.abstractmethod
    def sources(self) -> ta.Sequence[Source]:
        raise NotImplementedError

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return []


#


@dc.dataclass(frozen=True)
class UnaryOp(Op, lang.Abstract):
    x: Source

    @property
    def sources(self) -> ta.Sequence[Source]:
        return [self.x]


@dc.dataclass(frozen=True)
class Nop(UnaryOp):
    pass


@dc.dataclass(frozen=True)
class Exp2(UnaryOp):
    pass


@dc.dataclass(frozen=True)
class Log2(UnaryOp):
    pass


@dc.dataclass(frozen=True)
class Cast(UnaryOp):
    dtype: Dtype

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.dtype]


@dc.dataclass(frozen=True)
class Sin(UnaryOp):
    pass


@dc.dataclass(frozen=True)
class Recip(UnaryOp):
    pass


#


@dc.dataclass(frozen=True)
class BinaryOp(Op, lang.Abstract):
    x: Source
    y: Source

    @property
    def sources(self) -> ta.Sequence[Source]:
        return [self.x, self.y]


@dc.dataclass(frozen=True)
class Add(BinaryOp):
    pass


@dc.dataclass(frozen=True)
class Sub(BinaryOp):
    pass


@dc.dataclass(frozen=True)
class Mul(BinaryOp):
    pass


@dc.dataclass(frozen=True)
class Div(BinaryOp):
    pass


@dc.dataclass(frozen=True)
class Pow(BinaryOp):
    pass


@dc.dataclass(frozen=True)
class CmpEq(BinaryOp):
    pass


@dc.dataclass(frozen=True)
class Maximum(BinaryOp):  # BinaryOps.MAX
    pass


@dc.dataclass(frozen=True)
class Mod(BinaryOp):
    pass


@dc.dataclass(frozen=True)
class CmpLt(BinaryOp):
    pass


#


@dc.dataclass(frozen=True)
class ReduceOp(Op, lang.Abstract):
    x: Source

    new_shape: Shape

    @property
    def sources(self) -> ta.Sequence[Source]:
        return [self.x]

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.new_shape]


@dc.dataclass(frozen=True)
class Sum(ReduceOp):
    pass


@dc.dataclass(frozen=True)
class Max(ReduceOp):
    pass


#


@dc.dataclass(frozen=True)
class MovementOp(Op, lang.Abstract):
    x: Source

    @property
    def sources(self) -> ta.Sequence[Source]:
        return [self.x]


@dc.dataclass(frozen=True)
class Reshape(MovementOp):
    new_shape: Shape

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.new_shape]


@dc.dataclass(frozen=True)
class Permute(MovementOp):
    axes: ta.Sequence[int]

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.axes]


@dc.dataclass(frozen=True)
class Expand(MovementOp):
    new_shape: Shape

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.new_shape]


@dc.dataclass(frozen=True)
class Pad(MovementOp):
    padding: ta.Sequence[ta.Tuple[int, int]]

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.padding]


@dc.dataclass(frozen=True)
class Shrink(MovementOp):
    bounds: ta.Sequence[ta.Tuple[int, int]]  # (l, r) per dim

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.bounds]


@dc.dataclass(frozen=True)
class Restride(MovementOp):  # MovementOps.STRIDE
    stride: Stride

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.stride]


#


@dc.dataclass(frozen=True)
class FusedOp(Op, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class MulAcc(FusedOp):
    x: Source

    new_shape: Shape

    @property
    def sources(self) -> ta.Sequence[Source]:
        return [self.x]

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.new_shape]


#


@dc.dataclass(frozen=True)
class LoadOp(Op, lang.Abstract):
    @property
    def sources(self) -> ta.Sequence[Source]:
        return []


@dc.dataclass(frozen=True)
class Empty(LoadOp):
    pass


@dc.dataclass(frozen=True)
class Rand(LoadOp):
    seed: int

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.seed]


@dc.dataclass(frozen=True)
class Const(LoadOp):
    c: ta.Any  # FIXME: float

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.c]


@dc.dataclass(frozen=True)
class From(LoadOp):
    buf: ta.Any  # FIXME: [LazyBuffer, weakref.Ref[LazyBuffer]]

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.buf]


@dc.dataclass(frozen=True)
class Contiguous(LoadOp):
    buf: ta.Any  # FIXME: [LazyBuffer, weakref.Ref[LazyBuffer]]

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.buf]


# CUSTOM = enum.auto()


###


from omlish import collections as col  # noqa

from . import ops as _ops  # noqa
from .lazy import Lazy  # noqa
from .lazy import LazyBuffer  # noqa
from .lazy import LazyOp  # noqa


_OP_CONVERTERS: ta.Mapping[_ops.Op, ta.Callable[[LazyOp], Op]] = {
    **{o: (lambda ot: lambda op: ot(convert_from_lazy(op.srcs[0])))(ot) for o, ot in [
        (_ops.UnaryOp.NOP, Nop),
        (_ops.UnaryOp.EXP2, Exp2),
        (_ops.UnaryOp.LOG2, Log2),
        (_ops.UnaryOp.SIN, Sin),
        (_ops.UnaryOp.RECIP, Recip),
    ]},
    _ops.UnaryOp.CAST: lambda op: Cast(convert_from_lazy(op.srcs[0]), check.isinstance(op.arg, Dtype)),

    **{o: (lambda ot: lambda op: ot(convert_from_lazy(op.srcs[0]), convert_from_lazy(op.srcs[1])))(ot) for o, ot in [
        (_ops.BinaryOp.ADD, Add),
        (_ops.BinaryOp.SUB, Sub),
        (_ops.BinaryOp.MUL, Mul),
        (_ops.BinaryOp.DIV, Div),
        (_ops.BinaryOp.POW, Pow),
        (_ops.BinaryOp.CMP_EQ, CmpEq),
        (_ops.BinaryOp.MAX, Maximum),
        (_ops.BinaryOp.MOD, Mod),
        (_ops.BinaryOp.CMP_LT, CmpLt),
    ]},

    **{o: (lambda ot: lambda op: ot(convert_from_lazy(op.srcs[0]), check.isinstance(op.arg, Shape)))(ot) for o, ot in [
        (_ops.ReduceOp.SUM, Sum),
        (_ops.ReduceOp.MAX, Max),
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


def convert_from_lazy(laz: Lazy) -> Source:
    if isinstance(laz, LazyOp):
        return convert_from_lazy_op(laz)
    if isinstance(laz, LazyBuffer):
        return Buffer(laz)
    raise TypeError(laz)
