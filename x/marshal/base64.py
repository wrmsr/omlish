import base64

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .factories import SpecMapFactory


class Base64MarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: bytes) -> str:
        return base64.b64encode(o).decode('utf-8')

    def unmarshal(self, ctx: UnmarshalContext, v: str) -> bytes:
        return base64.b64decode(v.encode('utf-8'))


BASE64_MARSHALER_UNMARSHALER = Base64MarshalerUnmarshaler()

BASE64_MARSHALER_FACTORY: MarshalerFactory = SpecMapFactory({bytes: BASE64_MARSHALER_UNMARSHALER})
BASE64_UNMARSHALER_FACTORY: UnmarshalerFactory = SpecMapFactory({bytes: BASE64_MARSHALER_UNMARSHALER})
