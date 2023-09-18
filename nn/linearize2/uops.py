"""
LOOP = auto()
END = auto()
SPECIAL = auto()  # loops can be global, local, or other # noqa: E702
DEFINE_GLOBAL = auto()
DEFINE_LOCAL = auto()
DEFINE_ACC = auto()  # this defines buffers # noqa: E702
LOAD = auto()
STORE = auto()
CONST = auto()
BARRIER = auto()  # noqa: E702
ALU = auto()
WMMA = auto()
CAST = auto()
GEP = auto()  # noqa: E702
"""
import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .. import ops
from .. import symbolic as sym
from ..dtypes import Dtype
from ..dtypes import Float32
from ..scalars import Scalar


@dc.dataclass(frozen=True)
class Uop(lang.Sealed, lang.Abstract):
    dtype: ta.Optional[Dtype]
    vin: ta.Sequence['Uop']


@dc.dataclass(frozen=True)
class Loop(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class End(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Special(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class DefineGlobal(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class DefineLocal(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class DefineAcc(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Load(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Store(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Const(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Barrier(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Alu(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Wmma(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Cast(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Gep(Uop, lang.Final):
    pass
