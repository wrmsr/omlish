import re
import uuid

from .. import check
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .factories import TypeMapFactory
from .values import Value


PATTERN = re.compile(r'([0-9A-Fa-f]{8}-([0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12})|([0-9A-Fa-f]{32})')


class UuidMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: uuid.UUID) -> Value:
        return str(o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> uuid.UUID:
        return uuid.UUID(check.isinstance(v, str).replace('-', ''))


UUID_MARSHALER_UNMARSHALER = UuidMarshalerUnmarshaler()

UUID_MARSHALER_FACTORY: MarshalerFactory = TypeMapFactory({uuid.UUID: UUID_MARSHALER_UNMARSHALER})
UUID_UNMARSHALER_FACTORY: UnmarshalerFactory = TypeMapFactory({uuid.UUID: UUID_MARSHALER_UNMARSHALER})
