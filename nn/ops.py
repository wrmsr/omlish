"""
TODO:
 - identity eq? identity cols?
"""
import abc
import typing as ta
import weakref

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .dims import Shape as _Shape
from .dims import Stride as _Stride
from .dtypes import Dtype as _Dtype
from .lazy import Lazy
from .scalars import SCALAR_TYPES
from .scalars import Scalar

if ta.TYPE_CHECKING:
    from . import buffers
else:
    buffers = lang.proxy_import('.buffers', __package__)


#


@dc.dataclass(frozen=True)
class Op(Lazy, lang.Abstract):
    @property
    @abc.abstractmethod
    def srcs(self) -> ta.Sequence[Lazy]:
        raise NotImplementedError

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return []

    @property
    def buffers(self) -> ta.Iterator['buffers.Buffer']:
        for s in self.srcs:
            if isinstance(s, Op):
                yield from s.buffers
            elif isinstance(s, buffers.Buffer):
                yield s

    @property
    def ops(self) -> ta.Iterator['Op']:
        yield self
        for s in self.srcs:
            if isinstance(s, Op):
                yield from s.ops


#


@dc.dataclass(frozen=True)
class UnaryOp(Op, lang.Abstract):
    x: Lazy = dc.field(coerce=check.of_isinstance(Lazy))

    @property
    def srcs(self) -> ta.Sequence[Lazy]:
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
    dtype: _Dtype

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.dtype]


@dc.dataclass(frozen=True)
class Sin(UnaryOp):
    pass


@dc.dataclass(frozen=True)
class Sqrt(UnaryOp):
    pass


@dc.dataclass(frozen=True)
class Recip(UnaryOp):
    pass


#


@dc.dataclass(frozen=True)
class BinaryOp(Op, lang.Abstract):
    x: Lazy = dc.field(coerce=check.of_isinstance(Lazy))
    y: Lazy = dc.field(coerce=check.of_isinstance(Lazy))

    @property
    def srcs(self) -> ta.Sequence[Lazy]:
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
class CmpLt(BinaryOp):
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
    x: Lazy = dc.field(coerce=check.of_isinstance(Lazy))

    new_shape: _Shape = dc.field(coerce=check.of_isinstance(_Shape))

    @property
    def srcs(self) -> ta.Sequence[Lazy]:
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
    x: Lazy = dc.field(coerce=check.of_isinstance(Lazy))

    @property
    def srcs(self) -> ta.Sequence[Lazy]:
        return [self.x]

    @property
    @abc.abstractmethod
    def arg(self) -> ta.Any:
        raise NotImplementedError

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.arg]


@dc.dataclass(frozen=True)
class Reshape(MovementOp):
    new_shape: _Shape = dc.field(coerce=check.of_isinstance(_Shape))

    @property
    def arg(self) -> _Shape:
        return self.new_shape


@dc.dataclass(frozen=True)
class Permute(MovementOp):
    axes: ta.Sequence[int]

    @property
    def arg(self) -> ta.Sequence[int]:
        return self.axes


@dc.dataclass(frozen=True)
class Expand(MovementOp):
    new_shape: _Shape = dc.field(coerce=check.of_isinstance(_Shape))

    @property
    def arg(self) -> _Shape:
        return self.new_shape


@dc.dataclass(frozen=True)
class Pad(MovementOp):
    padding: ta.Sequence[ta.Tuple[int, int]]

    @property
    def arg(self) -> ta.Sequence[ta.Tuple[int, int]]:
        return self.padding


@dc.dataclass(frozen=True)
class Shrink(MovementOp):
    bounds: ta.Sequence[ta.Tuple[int, int]]  # (l, r) per dim

    @property
    def arg(self) -> ta.Sequence[ta.Tuple[int, int]]:
        return self.bounds


@dc.dataclass(frozen=True)
class Restride(MovementOp):  # MovementOps.STRIDE
    stride: _Stride

    @property
    def arg(self) -> _Stride:
        return self.stride


#


@dc.dataclass(frozen=True)
class TernaryOp(Op, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class MulAcc(TernaryOp):
    x: Lazy = dc.field(coerce=check.of_isinstance(Lazy))

    new_shape: _Shape = dc.field(coerce=check.of_isinstance(_Shape))

    @property
    def srcs(self) -> ta.Sequence[Lazy]:
        return [self.x]

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.new_shape]


@dc.dataclass(frozen=True)
class Where(TernaryOp):
    x: Lazy
    y: Lazy
    z: Lazy

    @property
    def srcs(self) -> ta.Sequence[Lazy]:
        return [self.x, self.y, self.z]


#


@dc.dataclass(frozen=True)
class LoadOp(Op, lang.Abstract):
    @property
    def srcs(self) -> ta.Sequence[Lazy]:
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
    c: Scalar = dc.field(check=lambda c: isinstance(c, SCALAR_TYPES))

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return [self.c]


@dc.dataclass(frozen=True)
class From(LoadOp):
    buf: ta.Union['buffers.Buffer', weakref.ReferenceType['buffers.Buffer']] = dc.field(  # noqa
        check=lambda o: isinstance(o, (buffers.Buffer, weakref.ref)),
    )

    @property
    def srcs(self) -> ta.Sequence[Lazy]:
        return[self.buf() if isinstance(self.buf, weakref.ref) else self.buf]

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return []


@dc.dataclass(frozen=True)
class Contiguous(LoadOp):
    buf: ta.Union['buffers.Buffer', weakref.ReferenceType['buffers.Buffer']] = dc.field(  # noqa
        check=lambda o: isinstance(o, (buffers.Buffer, weakref.ref)),
    )

    @property
    def srcs(self) -> ta.Sequence[Lazy]:
        return[self.buf() if isinstance(self.buf, weakref.ref) else self.buf]

    @property
    def args(self) -> ta.Sequence[ta.Any]:
        return []
