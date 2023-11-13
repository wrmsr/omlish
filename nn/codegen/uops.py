from __future__ import annotations

import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..dtypes import DType


@dc.dataclass(frozen=True, eq=False)
class UOp(lang.Abstract):
    dtype: ta.Optional[DType]
    vin: tuple[UOp, ...]
    arg: ta.Any

    def __repr__(self):
        return (
            f"{str(type(self).__name__):20s}: "
            f"{str(self.dtype) if self.dtype is not None else '':25s} "
            f"{str([type(x).__name__ for x in self.vin]):32s} "
            f"{self.arg}"
        )


# bottom ones are asm only


@dc.dataclass(frozen=True, eq=False, repr=False)
class Loop(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class If(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class End(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Special(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class DefineGlobal(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class DefineLocal(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class DefineAcc(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Load(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Store(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Const(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Barrier(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Phi(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Alu(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Wmma(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Cast(UOp, lang.Final):
    pass


@dc.dataclass(frozen=True, eq=False, repr=False)
class Gep(UOp, lang.Final):
    pass
