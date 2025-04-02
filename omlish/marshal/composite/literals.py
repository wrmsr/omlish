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
class LiteralMarshaler(Marshaler):
    e: Marshaler
    vs: frozenset

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        return self.e.marshal(ctx, check.in_(o, self.vs))


class LiteralMarshalerFactory(SimpleMarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Literal)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        lty = check.isinstance(rty, rfl.Literal)
        ety = check.single(set(map(type, lty.args)))
        return LiteralMarshaler(ctx.make(ety), frozenset(lty.args))


@dc.dataclass(frozen=True)
class LiteralUnmarshaler(Unmarshaler):
    e: Unmarshaler
    vs: frozenset

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        return check.in_(self.e.unmarshal(ctx, v), self.vs)


class LiteralUnmarshalerFactory(SimpleUnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, rfl.Literal)

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        lty = check.isinstance(rty, rfl.Literal)
        ety = check.single(set(map(type, lty.args)))
        return LiteralUnmarshaler(ctx.make(ety), frozenset(lty.args))
