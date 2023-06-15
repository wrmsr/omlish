from omlish import dataclasses as dc
from omlish import lang

from .dtypes import Dtype


class Value(lang.Sealed, lang.Abstract):
    pass


class Buffer(Value):
    pass


@dc.dataclass(frozen=True)
class Op(Value, lang.Abstract):
    pass


#


@dc.dataclass(frozen=True)
class UnaryOp(Op, lang.Abstract):
    x: Value


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


@dc.dataclass(frozen=True)
class Sin(UnaryOp):
    pass


#


@dc.dataclass(frozen=True)
class BinaryOp(Op, lang.Abstract):
    x: Value
    y: Value


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
class Max(BinaryOp):
    pass


@dc.dataclass(frozen=True)
class Mod(BinaryOp):
    pass


@dc.dataclass(frozen=True)
class CmpLt(BinaryOp):
    pass


#


"""
    SUM = enum.auto()
    MAX = enum.auto()


class MovementOp(Op, enum.Enum):
    RESHAPE = enum.auto()  # arg: new_shape: Shape
    PERMUTE = enum.auto()
    EXPAND = enum.auto()
    PAD = enum.auto()  # arg: padding: [(left, right) for _ in shape]
    SHRINK = enum.auto()
    STRIDE = enum.auto()


class FusedOp(Op, enum.Enum):
    MUL_ACC = enum.auto()


class LoadOp(Op, enum.Enum):
    EMPTY = enum.auto()
    RAND = enum.auto()
    CONST = enum.auto()
    FROM = enum.auto()
    CONTIGUOUS = enum.auto()
    CUSTOM = enum.auto()
"""
