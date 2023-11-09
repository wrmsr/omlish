import base64

from .. import check
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .factories import TypeMapFactory
from .values import Value


class Base64MarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: bytes) -> str:
        return base64.b64encode(o).decode()

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> bytes:
        return base64.b64decode(check.isinstance(v, str).encode())


BASE64_MARSHALER_UNMARSHALER = Base64MarshalerUnmarshaler()

BASE64_MARSHALER_FACTORY: MarshalerFactory = TypeMapFactory({bytes: BASE64_MARSHALER_UNMARSHALER})
BASE64_UNMARSHALER_FACTORY: UnmarshalerFactory = TypeMapFactory({bytes: BASE64_MARSHALER_UNMARSHALER})
