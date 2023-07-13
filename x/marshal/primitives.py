import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .exc import UnhandledSpecException
from .values import Value


class PrimitiveMarshaler(Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if isinstance(o, int):
            return o
        raise UnhandledSpecException(type(o))
