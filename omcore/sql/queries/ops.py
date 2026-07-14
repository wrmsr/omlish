import enum


##


class OpKind(enum.Enum):
    CMP = enum.auto()
    ARITH = enum.auto()
    BIT = enum.auto()
    STR = enum.auto()
