from __future__ import annotations

import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..dtypes import DType


@dc.dataclass(frozen=True)
class UOp(lang.Abstract):
    dtype: ta.Optional[DType]
    vin: tuple[UOp, ...]
    arg: ta.Any

    def __repr__(self):
        return (
            f"{self.num:4d} "
            f"{str(type(self).__name__):20s}: "
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


# bottom ones are asm only


@dc.dataclass(frozen=True, eq=False)
class Loop(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class If(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class End(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Special(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class DefineGlobal(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class DefineLocal(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class DefineAcc(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Load(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Store(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Const(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Barrier(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Phi(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Alu(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Wmma(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Cast(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False)
class Gep(UOp, lang.Final):
    pass
