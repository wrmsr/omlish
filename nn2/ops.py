from __future__ import annotations

import enum
import typing as ta

if ta.TYPE_CHECKING:
    from .lazy import LazyBuffer


# these are the llops your accelerator must implement, along with toCpu
# the Enum class doesn't work with mypy, this is static. sorry it's ugly
# NOTE: MOD, CMPLT don't have to be implemented on vectors, just scalars
# NOTE: rdna3 only has RECIP and not DIV. DIV and POW are on the chopping block
class UnaryOps(enum.Enum):
    NOOP = enum.auto()
    EXP2 = enum.auto()
    LOG2 = enum.auto()
    CAST = enum.auto()
    SIN = enum.auto()
    SQRT = enum.auto()
    RECIP = enum.auto()
    NEG = enum.auto()  # noqa: E702


class BinaryOps(enum.Enum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    MAX = enum.auto()
    MOD = enum.auto()
    CMPLT = enum.auto()  # noqa: E702


class TernaryOps(enum.Enum):
    MULACC = enum.auto()
    WHERE = enum.auto()  # noqa: E702


class ReduceOps(enum.Enum):
    SUM = enum.auto()
    MAX = enum.auto()  # noqa: E702


class BufferOps(enum.Enum):
    MEM = enum.auto()
    CONST = enum.auto()  # noqa: E702


# Ops below this line are not allowed in ASTs
class MovementOps(enum.Enum):
    RESHAPE = enum.auto()
    PERMUTE = enum.auto()
    EXPAND = enum.auto()
    PAD = enum.auto()
    SHRINK = enum.auto()
    STRIDE = enum.auto()
    AS_STRIDED = enum.auto()  # noqa: E702


class LoadOps(enum.Enum):
    EMPTY = enum.auto()
    RAND = enum.auto()
    CONST = enum.auto()
    FROM = enum.auto()
    CONTIGUOUS = enum.auto()
    CUSTOM = enum.auto()  # noqa: E702


Op = ta.Union[UnaryOps, BinaryOps, ReduceOps, MovementOps, LoadOps, TernaryOps, BufferOps]
OpType = ta.Union[
    type[UnaryOps],
    type[BinaryOps],
    type[ReduceOps],
    type[MovementOps],
    type[LoadOps],
    type[TernaryOps],
    type[BufferOps],
]


class LazyOp:
    __slots__ = "op", "src", "arg", "buffers", "__weakref__"
    op: Op
    src: tuple[ta.Union[LazyOp, LazyBuffer], ...]
    arg: ta.Any
    buffers: tuple[LazyBuffer, ...]

    def __init__(
        self, op: Op, src: tuple[ta.Union[LazyOp, LazyBuffer], ...], arg: ta.Any = None
    ):
        self.op, self.src, self.arg, self.buffers = op, src, arg, ()
        # NOTE: the linearizer's key function maps the buffers to ints, and LOCAL_BUFFER is used. we don't care about
        # buffers in these cases
        try:
            for x in src:
                self.buffers += x.buffers
        except AttributeError:
            self.buffers = ()

    def __repr__(self):
        return f"LazyOp(op={self.op}, src={self.src}, arg={self.arg})"

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, LazyOp)
            and self.op is __value.op
            and self.src == __value.src
            and self.arg == __value.arg
        )

    def __hash__(self) -> int:
        return hash((self.op, self.src, self.arg))

    @property
    def key(self):
        return (
            self.op,
            tuple(map(lambda x: getattr(x, "key", x), self.src)),
            getattr(self.arg, "key", self.arg),
        )

    def map_buffers(
        self, real_srcs: ta.Mapping[LazyBuffer, ta.Union[LazyBuffer, LazyOp]]
    ) -> LazyOp:
        return LazyOp(
            self.op, tuple([y.map_buffers(real_srcs) for y in self.src]), self.arg
        )

    def get_lazyops(self) -> list[LazyOp]:
        return [self] + [item for x in self.src for item in x.get_lazyops()]

    def replace_with_movement_ops(
        self: LazyOp, ops: list[tuple[MovementOps, tuple[ta.Any, ...]]]
    ) -> "LazyBuffer":
        assert self.op in BinaryOps or self.op in UnaryOps or self.op in TernaryOps
        srcs = [z.replace_with_movement_ops(ops) for z in self.src]
        return srcs[0].e(self.op, *srcs[1:], arg=self.arg)  # type: ignore

    @property
    def st(self):
        raise NotImplementedError

    @property
    def children(self):
        raise NotImplementedError

    @property
    def shape(self):
        raise NotImplementedError

    @property
    def realized(self):
        raise NotImplementedError

    @property
    def optype(self):
        raise NotImplementedError

    def realize(self):
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
