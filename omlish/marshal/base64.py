import base64
import typing as ta

from .. import check
from .. import dataclasses as dc
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .factories import TypeMapFactory
from .values import Value


T = ta.TypeVar('T')


@dc.dataclass(frozen=True)
class Base64MarshalerUnmarshaler(Marshaler, Unmarshaler, ta.Generic[T]):
    ty: type[T]

    def marshal(self, ctx: MarshalContext, o: bytes) -> str:
        return base64.b64encode(o).decode()

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> T:
        return self.ty(base64.b64decode(check.isinstance(v, str).encode()))


BASE64_TYPES = (
    bytes,
    bytearray,
)

BASE64_MARSHALER_FACTORY: MarshalerFactory = TypeMapFactory({
    ty: Base64MarshalerUnmarshaler(ty) for ty in BASE64_TYPES
})
BASE64_UNMARSHALER_FACTORY: UnmarshalerFactory = TypeMapFactory({
    ty: Base64MarshalerUnmarshaler(ty) for ty in BASE64_TYPES
})
