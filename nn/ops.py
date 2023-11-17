"""
NOTE: MOD, CMPLT don't have to be implemented on vectors, just scalars
NOTE: rdna3 only has RECIP and not DIV. DIV and POW are on the chopping block
"""
from __future__ import annotations

import typing as ta

from omlish import cached
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

if ta.TYPE_CHECKING:
    from .lazy import LazyBuffer


@dc.dataclass(frozen=True)
class LazyOp(lang.Abstract):
    src: tuple[ta.Union[LazyOp, LazyBuffer], ...]
    arg: ta.Any = None

    def __repr__(self):
        return f"LazyOp(op={type(self).__name__}, src={self.src}, arg={self.arg})"

    @cached.nullary
    def buffers(self) -> tuple[LazyBuffer, ...]:
        return tuple(col.unique(b for x in self.src for b in x.buffers()))

    @cached.property
    def hash(self) -> int:
        return hash((type(self), self.src, self.arg))

    def __hash__(self):
        return self.hash

    @cached.property
    def key(self) -> tuple:
        return (
            type(self),
            tuple(map(lambda x: getattr(x, "key", x), self.src)),
            getattr(self.arg, "key", self.arg),
        )

    def map_buffers(
            self,
            real_srcs: ta.Mapping[LazyBuffer, ta.Union[LazyBuffer, LazyOp]]
    ) -> LazyOp:
        return type(self)(
            tuple([y.map_buffers(real_srcs) for y in self.src]), self.arg
        )

    def get_lazyops(self) -> list[LazyOp]:
        return [self] + [item for x in self.src for item in x.get_lazyops()]

    def replace_with_movement_ops(
            self,
            ops: list[tuple[type[MovementOp], tuple[ta.Any, ...]]]
    ) -> "LazyBuffer":
        assert isinstance(self, (BinaryOp, UnaryOp, TernaryOp))
        srcs = [z.replace_with_movement_ops(ops) for z in self.src]
        return srcs[0].e(type(self), *srcs[1:], arg=self.arg)  # type: ignore

    @property
    def st(self):
        raise NotImplementedError

    @property
    def realized(self):
        raise NotImplementedError

    @property
    def children(self):
        raise NotImplementedError

    # movement ops
    def reshape(self, _):
        raise NotImplementedError

    def pad(self, _):
        raise NotImplementedError

    def expand(self, _):
        raise NotImplementedError

    def permute(self, _):
        raise NotImplementedError

    def shrink(self, _):
        raise NotImplementedError

    def stride(self, _):
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class UnaryOp(LazyOp, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Nop(UnaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Exp2(UnaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Log2(UnaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Cast(UnaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Sin(UnaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Sqrt(UnaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Recip(UnaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Neg(UnaryOp, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
class BinaryOp(LazyOp, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Add(BinaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Sub(BinaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Mul(BinaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Div(BinaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Max2(BinaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Mod(BinaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class CmpLt(BinaryOp, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
class TernaryOp(LazyOp, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class MulAcc(TernaryOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Where(TernaryOp, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
class ReduceOp(LazyOp, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Sum(ReduceOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Max(ReduceOp, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
class BufferOp(LazyOp, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Mem(BufferOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Const(BufferOp, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
class MovementOp(LazyOp, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Reshape(MovementOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Permute(MovementOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Expand(MovementOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Pad(MovementOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Shrink(MovementOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Restride(MovementOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class AsStrided(MovementOp, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
class LoadOp(LazyOp, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Empty(LoadOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Rand(LoadOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class LoadConst(LoadOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class From(LoadOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Contiguous(LoadOp, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Custom(LoadOp, lang.Final):
    pass
