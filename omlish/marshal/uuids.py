import re
import uuid

from .. import check
from .base import MarshalContext
from .base import Marshaler
from .base import TypeMapMarshalerFactory
from .base import TypeMapUnmarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .values import Value


PATTERN = re.compile(r'([0-9A-Fa-f]{8}-([0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12})|([0-9A-Fa-f]{32})')


class UuidMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: uuid.UUID) -> Value:
        return str(o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> uuid.UUID:
        return uuid.UUID(check.isinstance(v, str).replace('-', ''))


UUID_MARSHALER_UNMARSHALER = UuidMarshalerUnmarshaler()

UUID_MARSHALER_FACTORY = TypeMapMarshalerFactory({uuid.UUID: UUID_MARSHALER_UNMARSHALER})
UUID_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({uuid.UUID: UUID_MARSHALER_UNMARSHALER})
