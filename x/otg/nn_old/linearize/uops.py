"""
TODO:
 - DEFINE_GLOBAL
 - WMMA
 - SPECIAL
 - DEFINE_REGISTER
 - LABEL
 - COND_BRANCH
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


##


@dc.dataclass(frozen=True)
class Token:
    name: str
    dtype: Dtype
    offset: ta.Optional[int] = None

    def __repr__(self) -> str:
        return (
            f'<{self.name}>'
            if self.offset is None and self.dtype == Float32
            else f'<{self.name}:{self.dtype.name}:{self.offset}>'
        )


##


class Masked(lang.Abstract):
    @property
    @abc.abstractmethod
    def valid(self) -> sym.Var:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def invalid_value(self) -> Scalar:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class Uop(lang.Sealed, lang.Abstract):
    out: ta.Optional[Token]
    vin: ta.List[Token]


@dc.dataclass(frozen=True)
class Const(Uop, Masked):
    v: float

    valid: sym.Var = dc.field(override=True)  # type: ignore
    invalid_value: Scalar = dc.field(default=0., override=True)  # type: ignore


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
class MemOp(Uop, Masked, lang.Abstract):
    name: str
    idx: sym.Var
    local: bool
    dtype: Dtype

    valid: sym.Var = dc.field(override=True)  # type: ignore
    invalid_value: Scalar = dc.field(default=0., override=True)  # type: ignore


@dc.dataclass(frozen=True)
class Load(MemOp):
    pass


@dc.dataclass(frozen=True)
class Store(MemOp):
    pass
