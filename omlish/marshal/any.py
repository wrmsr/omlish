import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .factories import TypeMapFactory
from .values import Value


class AnyMarshalerUnmarshaler(Marshaler, Unmarshaler):

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return ctx.make(type(o)).marshal(ctx, o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return v


ANY_MARSHALER_UNMARSHALER = AnyMarshalerUnmarshaler()

ANY_MARSHALER_FACTORY: MarshalerFactory = TypeMapFactory({ta.Any: ANY_MARSHALER_UNMARSHALER})  # type: ignore
ANY_UNMARSHALER_FACTORY: UnmarshalerFactory = TypeMapFactory({ta.Any: ANY_MARSHALER_UNMARSHALER})  # type: ignore
