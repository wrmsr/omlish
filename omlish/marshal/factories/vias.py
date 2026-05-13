import typing as ta

from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.vias import MarshalVia
from ..api.vias import UnmarshalVia
from ..api.vias import make_marshaler_via
from ..api.vias import make_unmarshaler_via


##


class ViaConfigMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (via := ctx.configs.get(rty).get(MarshalVia)) is None:
            return None

        return lambda: make_marshaler_via(ctx, rty, via)


class ViaConfigUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (via := ctx.configs.get(rty).get(UnmarshalVia)) is None:
            return None

        return lambda: make_unmarshaler_via(ctx, rty, via)
