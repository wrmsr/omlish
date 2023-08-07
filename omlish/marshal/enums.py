import dataclasses as dc
import enum
import typing as ta

from .. import check
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .specs import Spec
from .values import Value


@dc.dataclass(frozen=True)
class EnumMarshaler(Marshaler):
    ty: ta.Type[enum.Enum]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o.name


class EnumMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, spec: Spec) -> ta.Optional[Marshaler]:
        if isinstance(spec, type) and issubclass(spec, enum.Enum):
            return EnumMarshaler(spec)
        return None


@dc.dataclass(frozen=True)
class EnumUnmarshaler(Unmarshaler):
    ty: ta.Type[enum.Enum]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.ty[check.isinstance(v, str)]


class EnumUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, spec: Spec) -> ta.Optional[Unmarshaler]:
        if isinstance(spec, type) and issubclass(spec, enum.Enum):
            return EnumUnmarshaler(spec)
        return None
