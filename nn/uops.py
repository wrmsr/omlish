import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from . import ops
from . import symbolic as sym
from .dtypes import Dtype


##


@dc.dataclass(frozen=True)
class Token:
    name: str
    dtype: Dtype
    offset: ta.Optional[int] = None


##


@dc.dataclass(frozen=True)
class Uop(lang.Sealed, lang.Abstract):
    out: ta.Optional[Token]
    vin: ta.List[Token]


@dc.dataclass(frozen=True)
class Const(Uop):
    v: float


@dc.dataclass(frozen=True)
class Cast(Uop):
    pass


@dc.dataclass(frozen=True)
class Alu(Uop):
    ty: ta.Type[ops.Op]


@dc.dataclass(frozen=True)
class DefineLocal(Uop):
    s: str
    sz: int


@dc.dataclass(frozen=True)
class Barrier(Uop):
    pass


#


@dc.dataclass(frozen=True)
class LoopOp(Uop, lang.Abstract):
    idxs: ta.Sequence[sym.Var]
    s: str


@dc.dataclass(frozen=True)
class Loop(LoopOp):
    pass


@dc.dataclass(frozen=True)
class EndLoop(LoopOp):
    pass


#


@dc.dataclass(frozen=True)
class MemOp(Uop, lang.Abstract):
    i: int
    idx: sym.Var
    valid: sym.Var


@dc.dataclass(frozen=True)
class Load(MemOp):
    pass


@dc.dataclass(frozen=True)
class Store(MemOp):
    pass
