import re
import typing as ta
import uuid

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .specs import Spec
from .values import Value


PATTERN = re.compile(r'([0-9A-Fa-f]{8}-([0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12})|([0-9A-Fa-f]{32})')


class UuidMarshaler(Marshaler):
    def marshal(self, ctx: MarshalContext, o: uuid.UUID) -> Value:
        return str(o)


class UuidMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, spec: Spec) -> ta.Optional[Marshaler]:
        if spec is uuid.UUID:
            return UuidMarshaler()
        return None
