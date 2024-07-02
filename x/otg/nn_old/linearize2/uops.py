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
    args: ta.Sequence[ta.Any]


@dc.dataclass(frozen=True)
class DefineGlobal(Uop, lang.Final):
    name: str
    elem_dtype: Dtype


@dc.dataclass(frozen=True)
class DefineLocal(Uop, lang.Final):
    name: str
    sz: int


@dc.dataclass(frozen=True)
class DefineAcc(Uop, lang.Final):
    init: float


@dc.dataclass(frozen=True)
class Load(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Store(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Const(Uop, lang.Final):
    v: Scalar


@dc.dataclass(frozen=True)
class Barrier(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Alu(Uop, lang.Final):
    ty: ta.Type[ops.Op]


@dc.dataclass(frozen=True)
class Wmma(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Cast(Uop, lang.Final):
    pass


@dc.dataclass(frozen=True)
class Gep(Uop, lang.Final):
    idx: int
