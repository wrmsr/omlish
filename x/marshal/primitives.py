import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .exc import UnhandledSpecException
from .values import Value


PRIMITIVE_TYPES: ta.Tuple[type, ...] = (
    type(None),
    bool,
    int,
    float,
    str,
    bytes,
)


class PrimitiveMarshaler(Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if isinstance(o, PRIMITIVE_TYPES):
            return o
        raise UnhandledSpecException(type(o))
