import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import TypeMapMarshalerFactory
from .base import TypeMapUnmarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .values import Value


##


PRIMITIVE_TYPES: tuple[type, ...] = (
    bool,
    int,
    float,
    str,
    bytes,
    type(None),
)


##


class PrimitiveMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if isinstance(o, PRIMITIVE_TYPES):
            return o  # type: ignore
        raise TypeError(o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        if isinstance(v, PRIMITIVE_TYPES):
            return v
        raise TypeError(v)


PRIMITIVE_MARSHALER_UNMARSHALER = PrimitiveMarshalerUnmarshaler()

PRIMITIVE_MARSHALER_FACTORY = TypeMapMarshalerFactory({  # noqa
    t: PRIMITIVE_MARSHALER_UNMARSHALER for t in PRIMITIVE_TYPES
})

PRIMITIVE_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({  # noqa
    t: PRIMITIVE_MARSHALER_UNMARSHALER for t in PRIMITIVE_TYPES
})
