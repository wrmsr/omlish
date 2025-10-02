import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory


##


@dc.dataclass(frozen=True)
class TypeMapMarshalerFactory(MarshalerFactory):
    m: ta.Mapping[rfl.Type, Marshaler | MarshalerFactory] = dc.xfield(
        default_factory=dict,
        coerce=lambda d: {
            check.isinstance(k, rfl.TYPES): check.isinstance(v, (Marshaler, UnmarshalerFactory))
            for k, v in d.items()
        },
    )

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        check.isinstance(rty, rfl.TYPES)
        try:
            m = self.m[rty]
        except KeyError:
            return None

        if isinstance(m, Marshaler):
            return lambda: m
        elif isinstance(m, MarshalerFactory):
            return m.make_marshaler(ctx, rty)
        else:
            raise TypeError(m)


@dc.dataclass(frozen=True)
class TypeMapUnmarshalerFactory(UnmarshalerFactory):
    u: ta.Mapping[rfl.Type, Unmarshaler | UnmarshalerFactory] = dc.xfield(
        default_factory=dict,
        coerce=lambda d: {
            check.isinstance(k, rfl.TYPES): check.isinstance(v, (Unmarshaler, UnmarshalerFactory))
            for k, v in d.items()
        },
    )

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        check.isinstance(rty, rfl.TYPES)
        try:
            u = self.u[rty]
        except KeyError:
            return None

        if isinstance(u, Unmarshaler):
            return lambda: u
        elif isinstance(u, UnmarshalerFactory):
            return u.make_unmarshaler(ctx, rty)
        else:
            raise TypeError(u)
