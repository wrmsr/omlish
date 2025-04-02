"""
FIXME:
 - don't base64 by default, only for json-esque targets
"""
import base64
import typing as ta

from ... import check
from ... import dataclasses as dc
from ..base import MarshalContext
from ..base import Marshaler
from ..base import TypeMapMarshalerFactory
from ..base import TypeMapUnmarshalerFactory
from ..base import UnmarshalContext
from ..base import Unmarshaler
from ..values import Value


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class Base64MarshalerUnmarshaler(Marshaler, Unmarshaler, ta.Generic[T]):
    ty: type[T]

    def marshal(self, ctx: MarshalContext, o: bytes) -> str:
        return base64.b64encode(o).decode()

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> T:
        return self.ty(base64.b64decode(check.isinstance(v, str).encode()))  # type: ignore


BASE64_TYPES = (
    bytes,
    bytearray,
)

BASE64_MARSHALER_FACTORY = TypeMapMarshalerFactory({
    ty: Base64MarshalerUnmarshaler(ty) for ty in BASE64_TYPES
})

BASE64_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({
    ty: Base64MarshalerUnmarshaler(ty) for ty in BASE64_TYPES
})
