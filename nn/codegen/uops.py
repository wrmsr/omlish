from __future__ import annotations

import typing as ta
import enum

from ..dtypes import DType


# bottom ones are asm only
class UOps(enum.Enum):
    LOOP = enum.auto()
    IF = enum.auto()
    END = enum.auto()
    SPECIAL = enum.auto()  # loops can be global, local, or other # noqa: E702
    DEFINE_GLOBAL = enum.auto()
    DEFINE_LOCAL = enum.auto()
    DEFINE_ACC = enum.auto()  # this defines buffers # noqa: E702
    LOAD = enum.auto()
    STORE = enum.auto()
    CONST = enum.auto()
    BARRIER = enum.auto()  # noqa: E702
    PHI = enum.auto()
    ALU = enum.auto()
    WMMA = enum.auto()
    CAST = enum.auto()
    GEP = enum.auto()  # noqa: E702


class UOp(ta.NamedTuple):
    uop: UOps
    dtype: ta.Optional[DType]
    vin: tuple[UOp, ...]
    arg: ta.Any

    def __repr__(self):
        return (
            f"{self.num:4d} "
            f"{str(self.uop):20s}: "
            f"{str(self.dtype) if self.dtype is not None else '':25s} "
            f"{str([x.num for x in self.vin]):32s} "
            f"{self.arg}"
        )

    # UOps are unique
    num: int

    def __hash__(self):
        return self.num

    def __eq__(self, x):
        return self.num == x.num
