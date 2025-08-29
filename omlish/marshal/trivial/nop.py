import typing as ta

from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..base.values import Value


##


class NopMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o  # noqa

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return v


NOP_MARSHALER_UNMARSHALER = NopMarshalerUnmarshaler()
