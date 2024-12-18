import dataclasses as dc
import typing as ta

from .. import check
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .values import Value


@dc.dataclass(frozen=True)
class LiteralMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        return self.e.marshal(ctx, o)


class LiteralMarshalerFactory(MarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Literal)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        lty = check.isinstance(rty, rfl.Literal)
        ety = check.single(set(map(type, lty.args)))
        return LiteralMarshaler(ctx.make(ety))


@dc.dataclass(frozen=True)
class LiteralUnmarshaler(Unmarshaler):
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        return self.e.unmarshal(ctx, v)


class LiteralUnmarshalerFactory(UnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Literal)

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        lty = check.isinstance(rty, rfl.Literal)
        ety = check.single(set(map(type, lty.args)))
        return LiteralUnmarshaler(ctx.make(ety))
