import typing as ta

from ... import dataclasses as dc
from ..api.contexts import MarshalContext
from ..api.contexts import UnmarshalContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value


##


@dc.dataclass(frozen=True)
class WrappedMarshaler(Marshaler):
    wrapper: ta.Callable[[MarshalContext, ta.Any], ta.Any]
    m: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return self.m.marshal(ctx, self.wrapper(ctx, o))


@dc.dataclass(frozen=True)
class WrappedUnmarshaler(Unmarshaler):
    unwrapper: ta.Callable[[UnmarshalContext, ta.Any], ta.Any]
    u: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.unwrapper(ctx, self.u.unmarshal(ctx, v))
