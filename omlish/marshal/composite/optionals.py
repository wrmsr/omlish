import dataclasses as dc
import typing as ta

from ... import check
from ... import reflect as rfl
from ..base import MarshalContext
from ..base import Marshaler
from ..base import SimpleMarshalerFactory
from ..base import SimpleUnmarshalerFactory
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..values import Value


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
