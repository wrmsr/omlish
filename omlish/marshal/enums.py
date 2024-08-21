import dataclasses as dc
import enum
import typing as ta

from .. import check
from .. import matchfns as mfs
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
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and issubclass(rty, enum.Enum)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        if not isinstance(rty, type) and issubclass(rty, enum.Enum):
            raise mfs.MatchGuardError(ctx, rty)
        return EnumMarshaler(rty)


@dc.dataclass(frozen=True)
class EnumUnmarshaler(Unmarshaler):
    ty: type[enum.Enum]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.ty[check.isinstance(v, str)]


class EnumUnmarshalerFactory(UnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and issubclass(rty, enum.Enum)

    def __call__(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler | None:

        if isinstance(rty, type) and issubclass(rty, enum.Enum):
            return EnumUnmarshaler(rty)
        return None
