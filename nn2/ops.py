"""
NOTE: MOD, CMPLT don't have to be implemented on vectors, just scalars
NOTE: rdna3 only has RECIP and not DIV. DIV and POW are on the chopping block
"""
from __future__ import annotations

import typing as ta

from omlish import lang

if ta.TYPE_CHECKING:
    from .lazy import LazyBuffer


class LazyOp(lang.Abstract):
    src: tuple[ta.Union[LazyOp, LazyBuffer], ...]
    arg: ta.Any
    buffers: tuple[LazyBuffer, ...]

    def __init__(
            self,
            src: tuple[ta.Union[LazyOp, LazyBuffer], ...],
            arg: ta.Any = None,
    ) -> None:
        super().__init__()

        self.src = src
        self.arg = arg
        self.buffers = ()

        # NOTE: the linearizer's key function maps the buffers to ints, and LOCAL_BUFFER is used. we don't care about
        # buffers in these cases
        try:
            for x in src:
                self.buffers += x.buffers
        except AttributeError:
            self.buffers = ()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(src={self.src}, arg={self.arg})"

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, LazyOp)
            and type(self) is type(__value)
            and self.src == __value.src
            and self.arg == __value.arg
        )

    def __hash__(self) -> int:
        return hash((type(self), self.src, self.arg))

    @property
    def key(self):
        return (
            type(self),
            tuple(map(lambda x: getattr(x, "key", x), self.src)),
            getattr(self.arg, "key", self.arg),
        )

    def map_buffers(
            self,
            real_srcs: ta.Mapping[ta.Any, ta.Union[LazyBuffer, LazyOp]]
    ) -> LazyOp:
        return type(self)(
            tuple([y.map_buffers(real_srcs) if y not in real_srcs else real_srcs[y] for y in self.src]), self.arg
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
    def shape(self):
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


class UnaryOp(LazyOp, lang.Abstract):
    pass


class Nop(UnaryOp, lang.Final):
    pass


class Exp2(UnaryOp, lang.Final):
    pass


class Log2(UnaryOp, lang.Final):
    pass


class Cast(UnaryOp, lang.Final):
    pass


class Sin(UnaryOp, lang.Final):
    pass


class Sqrt(UnaryOp, lang.Final):
    pass


class Recip(UnaryOp, lang.Final):
    pass


class Neg(UnaryOp, lang.Final):
    pass


##


class BinaryOp(LazyOp, lang.Abstract):
    pass


class Add(BinaryOp, lang.Final):
    pass


class Sub(BinaryOp, lang.Final):
    pass


class Mul(BinaryOp, lang.Final):
    pass


class Div(BinaryOp, lang.Final):
    pass


class Max2(BinaryOp, lang.Final):
    pass


class Mod(BinaryOp, lang.Final):
    pass


class CmpLt(BinaryOp, lang.Final):
    pass


##


class TernaryOp(LazyOp, lang.Abstract):
    pass


class MulAcc(TernaryOp, lang.Final):
    pass


class Where(TernaryOp, lang.Final):
    pass


##


class ReduceOp(LazyOp, lang.Abstract):
    pass


class Sum(ReduceOp, lang.Final):
    pass


class Max(ReduceOp, lang.Final):
    pass


##


class BufferOp(LazyOp, lang.Abstract):
    pass


class Mem(BufferOp, lang.Final):
    pass


class Const(BufferOp, lang.Final):
    pass


##


class MovementOp(LazyOp, lang.Abstract):
    pass


class Reshape(MovementOp, lang.Final):
    pass


class Permute(MovementOp, lang.Final):
    pass


class Expand(MovementOp, lang.Final):
    pass


class Pad(MovementOp, lang.Final):
    pass


class Shrink(MovementOp, lang.Final):
    pass


class Restride(MovementOp, lang.Final):
    pass


class AsStrided(MovementOp, lang.Final):
    pass


##


class LoadOp(LazyOp, lang.Abstract):
    pass


class Empty(LoadOp, lang.Final):
    pass


class Rand(LoadOp, lang.Final):
    pass


class LoadConst(LoadOp, lang.Final):
    pass


class From(LoadOp, lang.Final):
    pass


class Contiguous(LoadOp, lang.Final):
    pass


class Custom(LoadOp, lang.Final):
    pass
