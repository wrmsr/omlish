import dataclasses as dc
import typing as ta

from ... import check
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..base.values import Value


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
        if not (isinstance(rty, rfl.Union) and rty.is_optional):
            return None
        return lambda: OptionalMarshaler(ctx.make_marshaler(check.isinstance(rty, rfl.Union).without_none()))


@dc.dataclass(frozen=True)
class OptionalUnmarshaler(Unmarshaler):
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        if v is None:
            return None
        return self.e.unmarshal(ctx, v)


class OptionalUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, rfl.Union) and rty.is_optional):
            return None
        return lambda: OptionalUnmarshaler(ctx.make_unmarshaler(check.isinstance(rty, rfl.Union).without_none()))
