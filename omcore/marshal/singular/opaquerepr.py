import typing as ta

from ... import check
from ... import lang
from ..api.contexts import MarshalContext
from ..api.contexts import UnmarshalContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value
from ..factories.typemap import TypeMapMarshalerFactory
from ..factories.typemap import TypeMapUnmarshalerFactory


##


class OpaqueReprMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if not isinstance(o, lang.OpaqueRepr):
            o = lang.OpaqueRepr(repr(o))
        return o

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return lang.OpaqueRepr(check.isinstance(v, str))


OPAQUE_REPR_MARSHALER_FACTORY = TypeMapMarshalerFactory({lang.OpaqueRepr: OpaqueReprMarshalerUnmarshaler()})
OPAQUE_REPR_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({lang.OpaqueRepr: OpaqueReprMarshalerUnmarshaler()})
