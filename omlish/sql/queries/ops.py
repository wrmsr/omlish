import enum


class OpKind(enum.Enum):
    ARITH = enum.auto()
    BIT = enum.auto()
    CMP = enum.auto()
