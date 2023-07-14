import dataclasses as dc
import enum
import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
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
