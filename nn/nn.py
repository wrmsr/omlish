"""
class UnaryOps(Enum):
    NOOP = auto()
    EXP = auto()
    LOG = auto()
    CAST = auto()


class BinaryOps(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()
    CMP_EQ = auto()
    MAX = auto()


class ReduceOps(Enum):
    SUM = auto()
    MAX = auto()


class FusedOps(Enum):
    MUL_ACC = auto()


class LoadOps(Enum):
    FROM_CPU = auto()
    CONTIGUOUS = auto()
    TO_CPU = auto()
    CUSTOM = auto()


class MovementOps(Enum):
    RESHAPE = auto()
    PERMUTE = auto()
    EXPAND = auto()
    PAD = auto()
    SHRINK = auto()
    STRIDE = auto()
"""
import numpy as np  # noqa


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
