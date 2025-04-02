import typing as ta

from ..base import MarshalContext
from ..base import Marshaler
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..values import Value


##


class NopMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o  # noqa

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return v


NOP_MARSHALER_UNMARSHALER = NopMarshalerUnmarshaler()
