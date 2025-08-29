import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ...funcs import match as mfs
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import MarshalerMaker
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..base.types import UnmarshalerMaker


R = ta.TypeVar('R')
C = ta.TypeVar('C')


##


@dc.dataclass(frozen=True)
class _TypeMapFactory(mfs.MatchFn[[C, rfl.Type], R]):
    m: ta.Mapping[rfl.Type, R] = dc.field(default_factory=dict)

    def __post_init__(self) -> None:
        for k in self.m:
            if not isinstance(k, rfl.TYPES):
                raise TypeError(k)

    def guard(self, ctx: C, rty: rfl.Type) -> bool:
        check.isinstance(rty, rfl.TYPES)
        return rty in self.m

    def fn(self, ctx: C, rty: rfl.Type) -> R:
        check.isinstance(rty, rfl.TYPES)
        try:
            return self.m[rty]
        except KeyError:
            raise mfs.MatchGuardError(ctx, rty)  # noqa


##


@dc.dataclass(frozen=True)
class TypeMapMarshalerFactory(
    _TypeMapFactory[MarshalContext, Marshaler],
    MarshalerFactory,
):
    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self  # noqa


@dc.dataclass(frozen=True)
class TypeMapUnmarshalerFactory(
    _TypeMapFactory[UnmarshalContext, Unmarshaler],
    UnmarshalerFactory,
):
    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self  # noqa
