import dataclasses as dc
import enum
import typing as ta

from ... import check
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..base.values import Value
from ..factories.simple import SimpleMarshalerFactory
from ..factories.simple import SimpleUnmarshalerFactory


##


@dc.dataclass(frozen=True)
class EnumMarshaler(Marshaler):
    ty: type[enum.Enum]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o.name


class EnumMarshalerFactory(SimpleMarshalerFactory):
    def guard(self, ctx: MarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and issubclass(rty, enum.Enum)

    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        ty = check.isinstance(rty, type)
        check.state(issubclass(ty, enum.Enum))
        return EnumMarshaler(ty)  # noqa


@dc.dataclass(frozen=True)
class EnumUnmarshaler(Unmarshaler):
    ty: type[enum.Enum]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.ty[check.isinstance(v, str)]


class EnumUnmarshalerFactory(SimpleUnmarshalerFactory):
    def guard(self, ctx: UnmarshalContext, rty: rfl.Type) -> bool:
        return isinstance(rty, type) and issubclass(rty, enum.Enum)

    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        ty = check.isinstance(rty, type)
        check.state(issubclass(ty, enum.Enum))
        return EnumUnmarshaler(ty)
