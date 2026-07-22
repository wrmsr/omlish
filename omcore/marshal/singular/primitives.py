"""
TODO:
 - bytes Option
 - field-configurable coercion
"""
import typing as ta

from ... import dataclasses as dc
from ..api.contexts import MarshalContext
from ..api.contexts import UnmarshalContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value
from ..factories.typemap import TypeMapMarshalerFactory
from ..factories.typemap import TypeMapUnmarshalerFactory
from .api import PRIMITIVE_TYPES


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
