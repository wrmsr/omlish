import typing as ta

from ..api.contexts import MarshalContext
from ..api.contexts import UnmarshalContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value
from ..factories.typemap import TypeMapMarshalerFactory
from ..factories.typemap import TypeMapUnmarshalerFactory


##


class CannotUnmarshalOpaqueReprNotError(TypeError):
    pass


class OpaqueRepr:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


class OpaqueReprMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        raise NotImplementedError

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        raise CannotUnmarshalOpaqueReprNotError


OPAQUE_REPR_MARSHALER_FACTORY = TypeMapMarshalerFactory({OpaqueRepr: OpaqueReprMarshalerUnmarshaler()})
OPAQUE_REPR_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({OpaqueRepr: OpaqueReprMarshalerUnmarshaler()})
