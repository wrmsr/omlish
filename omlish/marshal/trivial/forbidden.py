import dataclasses as dc
import typing as ta

from ... import reflect as rfl
from ...funcs import match as mfs
from ..base import MarshalContext
from ..base import Marshaler
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..exceptions import ForbiddenTypeError


C = ta.TypeVar('C')
R = ta.TypeVar('R')


@dc.dataclass(frozen=True)
class ForbiddenTypeFactory(mfs.MatchFn[[C, rfl.Type], R]):
    rtys: ta.AbstractSet[rfl.Type]

    def guard(self, ctx: C, rty: rfl.Type) -> bool:
        return rty in self.rtys

    def fn(self, ctx: C, rty: rfl.Type) -> R:
        raise ForbiddenTypeError(rty)


@dc.dataclass(frozen=True)
class ForbiddenTypeMarshalerFactory(ForbiddenTypeFactory[MarshalContext, Marshaler]):
    pass


@dc.dataclass(frozen=True)
class ForbiddenTypeUnmarshalerFactory(ForbiddenTypeFactory[UnmarshalContext, Unmarshaler]):
    pass
