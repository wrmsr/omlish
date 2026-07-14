import typing as ta

from ..api.contexts import MarshalContext
from ..api.contexts import UnmarshalContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value


##


class NopMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o  # noqa

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return v


NOP_MARSHALER_UNMARSHALER = NopMarshalerUnmarshaler()
