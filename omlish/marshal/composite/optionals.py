import dataclasses as dc
import typing as ta

from ... import check
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..base.values import Value
from ..factories.simple import SimpleMarshalerFactory
from ..factories.simple import SimpleUnmarshalerFactory


##


@dc.dataclass(frozen=True)
class OptionalMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        if o is None:
            return None
        return self.e.marshal(ctx, o)


class OptionalMarshalerFactory(SimpleMarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Union) and rty.is_optional

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        return OptionalMarshaler(ctx.make(check.isinstance(rty, rfl.Union).without_none()))


@dc.dataclass(frozen=True)
class OptionalUnmarshaler(Unmarshaler):
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        if v is None:
            return None
        return self.e.unmarshal(ctx, v)


class OptionalUnmarshalerFactory(SimpleUnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Union) and rty.is_optional

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        return OptionalUnmarshaler(ctx.make(check.isinstance(rty, rfl.Union).without_none()))
