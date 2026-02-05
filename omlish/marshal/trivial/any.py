import typing as ta

from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import UnmarshalContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value
from ..factories.typemap import TypeMapMarshalerFactory
from ..factories.typemap import TypeMapUnmarshalerFactory


##


class AnyMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return ctx.marshal_factory_context.make_marshaler(type(o)).marshal(ctx, o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return v


ANY_MARSHALER_UNMARSHALER = AnyMarshalerUnmarshaler()

ANY_MARSHALER_FACTORY = TypeMapMarshalerFactory({rfl.ANY: ANY_MARSHALER_UNMARSHALER})
ANY_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({rfl.ANY: ANY_MARSHALER_UNMARSHALER})
