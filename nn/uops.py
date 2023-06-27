import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from . import ops2  # noqa
from . import symbolic as sym
from .dtypes import Dtype


##


@dc.dataclass(frozen=True)
class Token:
    name: str
    dtype: Dtype
    offset: ta.Optional[int] = None

    def render(self, with_type: bool = False) -> str:
        if with_type:
            check.none(self.offset)
            return f'{self.dtype.name} {self.name}'
        if self.offset is None:
            return self.name
        raise NotImplementedError


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
    ty: ta.Type[ops2.Op]


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
