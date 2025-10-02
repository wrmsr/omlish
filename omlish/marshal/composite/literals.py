"""
TODO:
 - squash literal unions - typing machinery doesn't
"""
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
class LiteralMarshaler(Marshaler):
    e: Marshaler
    vs: frozenset

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        return self.e.marshal(ctx, check.in_(o, self.vs))


class LiteralMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, rfl.Literal) and len(set(map(type, rty.args))) == 1):
            return None
        ety = check.single(set(map(type, rty.args)))
        return lambda: LiteralMarshaler(ctx.make_marshaler(ety), frozenset(rty.args))


@dc.dataclass(frozen=True)
class LiteralUnmarshaler(Unmarshaler):
    e: Unmarshaler
    vs: frozenset

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        return check.in_(self.e.unmarshal(ctx, v), self.vs)


class LiteralUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, rfl.Literal) and len(set(map(type, rty.args))) == 1):
            return None
        ety = check.single(set(map(type, rty.args)))
        return lambda: LiteralUnmarshaler(ctx.make_unmarshaler(ety), frozenset(rty.args))
