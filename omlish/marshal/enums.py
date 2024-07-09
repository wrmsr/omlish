import dataclasses as dc
import enum
import typing as ta

from .. import check
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .values import Value


@dc.dataclass(frozen=True)
class EnumMarshaler(Marshaler):
    ty: type[enum.Enum]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o.name


class EnumMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler | None:
        if isinstance(rty, type) and issubclass(rty, enum.Enum):
            return EnumMarshaler(rty)
        return None


@dc.dataclass(frozen=True)
class EnumUnmarshaler(Unmarshaler):
    ty: type[enum.Enum]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.ty[check.isinstance(v, str)]


class EnumUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler | None:
        if isinstance(rty, type) and issubclass(rty, enum.Enum):
            return EnumUnmarshaler(rty)
        return None
