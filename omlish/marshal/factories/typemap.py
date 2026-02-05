import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


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
