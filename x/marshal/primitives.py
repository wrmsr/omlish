import typing as ta

from .base import Marshaler
from .base import MarshalContext
from .values import Value


class PrimitiveMarshaler(Marshaler):
    def __call__(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if isinstance(o, int):
            return o
        raise TypeError(o)
