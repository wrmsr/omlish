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
    RESHAPE = enum.auto()
    PERMUTE = enum.auto()
    EXPAND = enum.auto()
    PAD = enum.auto()
    SHRINK = enum.auto()
    STRIDE = enum.auto()


class FusedOp(Op, enum.Enum):
    MUL_ACC = enum.auto()


class LoadOp(Op, enum.Enum):
    FROM_CPU = enum.auto()
    CONTIGUOUS = enum.auto()
    TO_CPU = enum.auto()
    CUSTOM = enum.auto()
