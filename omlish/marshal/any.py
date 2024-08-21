import typing as ta

from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import TypeMapMarshalerFactory
from .base import TypeMapUnmarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .values import Value


class AnyMarshalerUnmarshaler(Marshaler, Unmarshaler):

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return ctx.make(type(o)).marshal(ctx, o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return v


ANY_MARSHALER_UNMARSHALER = AnyMarshalerUnmarshaler()

ANY_MARSHALER_FACTORY = TypeMapMarshalerFactory({rfl.ANY: ANY_MARSHALER_UNMARSHALER})
ANY_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({rfl.ANY: ANY_MARSHALER_UNMARSHALER})
