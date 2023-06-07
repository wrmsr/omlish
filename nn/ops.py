"""
TODO:
 - case class hierarchy of ops w/ typed args
"""
import enum

from omlish import lang


class Op(lang.Sealed):
    pass


class UnaryOp(Op, enum.Enum):
    NOP = enum.auto()
    EXP = enum.auto()
    LOG = enum.auto()
    CAST = enum.auto()


class BinaryOp(Op, enum.Enum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    POW = enum.auto()
    CMP_EQ = enum.auto()
    MAX = enum.auto()


class ReduceOp(Op, enum.Enum):
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
