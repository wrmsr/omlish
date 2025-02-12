"""
TODO:
 - field-configurable coercion
"""
import typing as ta

from ... import dataclasses as dc
from ..base import MarshalContext
from ..base import Marshaler
from ..base import TypeMapMarshalerFactory
from ..base import TypeMapUnmarshalerFactory
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..values import Value


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


@dc.dataclass(frozen=True)
class PrimitiveMarshalerUnmarshaler(Marshaler, Unmarshaler):
    ty: type

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if isinstance(o, self.ty):
            return o  # type: ignore
        if isinstance(o, PRIMITIVE_TYPES):
            return self.ty(o)
        raise TypeError(o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        if isinstance(v, self.ty):
            return v
        if isinstance(v, PRIMITIVE_TYPES):
            return self.ty(v)
        raise TypeError(v)


PRIMITIVE_MARSHALER_FACTORY = TypeMapMarshalerFactory({  # noqa
    t: PrimitiveMarshalerUnmarshaler(t) for t in PRIMITIVE_TYPES
})

PRIMITIVE_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({  # noqa
    t: PrimitiveMarshalerUnmarshaler(t) for t in PRIMITIVE_TYPES
})
