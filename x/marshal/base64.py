import base64
import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .specs import Spec


class Base64MarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: bytes) -> str:
        return base64.b64encode(o).decode('utf-8')

    def unmarshal(self, ctx: UnmarshalContext, v: str) -> bytes:
        return base64.b64decode(v.encode('utf-8'))


class Base64MarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, spec: Spec) -> ta.Optional[Marshaler]:
        if spec is bytes:
            return Base64MarshalerUnmarshaler()
        return None
