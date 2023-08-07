import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .factories import SpecMapFactory
from .values import Value


PRIMITIVE_TYPES: ta.Tuple[type, ...] = (
    bool,
    int,
    float,
    str,
    bytes,
)


class PrimitiveMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if isinstance(o, PRIMITIVE_TYPES):
            return o
        raise TypeError(o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        if isinstance(v, PRIMITIVE_TYPES):
            return v
        raise TypeError(v)


PRIMITIVE_MARSHALER_UNMARSHALER = PrimitiveMarshalerUnmarshaler()

PRIMITIVE_MARSHALER_FACTORY: MarshalerFactory = SpecMapFactory({  # noqa
    t: PRIMITIVE_MARSHALER_UNMARSHALER for t in PRIMITIVE_TYPES
})

PRIMITIVE_UNMARSHALER_FACTORY: UnmarshalerFactory = SpecMapFactory({  # noqa
    t: PRIMITIVE_MARSHALER_UNMARSHALER for t in PRIMITIVE_TYPES
})
