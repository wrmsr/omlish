import typing as ta

from ... import dataclasses as dc
from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.values import Value


##


@dc.dataclass(frozen=True)
class OptionalMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        if o is None:
            return None
        return self.e.marshal(ctx, o)


class OptionalMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not rfl.is_optional(rty):
            return None
        return lambda: OptionalMarshaler(ctx.make_marshaler(rfl.strip_optional(rty)))


@dc.dataclass(frozen=True)
class OptionalUnmarshaler(Unmarshaler):
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        if v is None:
            return None
        return self.e.unmarshal(ctx, v)


class OptionalUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not rfl.is_optional(rty):
            return None
        return lambda: OptionalUnmarshaler(ctx.make_unmarshaler(rfl.strip_optional(rty)))
