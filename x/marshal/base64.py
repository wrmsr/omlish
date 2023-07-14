import base64
import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .specs import Spec
from .values import Value


class Base64Marshaler(Marshaler):
    def marshal(self, ctx: MarshalContext, o: bytes) -> Value:
        return base64.b64encode(o).decode('utf-8')


class Base64MarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, spec: Spec) -> ta.Optional[Marshaler]:
        if spec is bytes:
            return Base64Marshaler(spec)
        return None
