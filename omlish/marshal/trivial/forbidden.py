import dataclasses as dc
import typing as ta

from ... import reflect as rfl
from ...funcs import match as mfs
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.errors import ForbiddenTypeError
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..factories.simple import SimpleMarshalerFactory
from ..factories.simple import SimpleUnmarshalerFactory


C = ta.TypeVar('C')
R = ta.TypeVar('R')


##


@dc.dataclass(frozen=True)
class ForbiddenTypeFactory(mfs.MatchFn[[C, rfl.Type], R]):
    rtys: ta.AbstractSet[rfl.Type]

    def guard(self, ctx: C, rty: rfl.Type) -> bool:
        return rty in self.rtys

    def fn(self, ctx: C, rty: rfl.Type) -> R:
        raise ForbiddenTypeError(rty)


@dc.dataclass(frozen=True)
class ForbiddenTypeMarshalerFactory(
    ForbiddenTypeFactory[MarshalContext, Marshaler],
    SimpleMarshalerFactory,
):
    pass


@dc.dataclass(frozen=True)
class ForbiddenTypeUnmarshalerFactory(
    ForbiddenTypeFactory[UnmarshalContext, Unmarshaler],
    SimpleUnmarshalerFactory,
):
    pass
