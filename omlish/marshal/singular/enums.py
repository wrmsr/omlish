"""
TODO:
 - chain value marshal/unmarshal? only for known value typed enums?
"""
import enum
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.values import Value


##


@dc.dataclass(frozen=True)
class EnumNameMarshaler(Marshaler):
    ty: type[enum.Enum]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o.name


@dc.dataclass(frozen=True)
class EnumNameUnmarshaler(Unmarshaler):
    ty: type[enum.Enum]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.ty[check.isinstance(v, str)]


##

@dc.dataclass(frozen=True)
class EnumValueMarshaler(Marshaler):
    ty: type[enum.Enum]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o.value


@dc.dataclass(frozen=True)
class EnumValueUnmarshaler(Unmarshaler):
    ty: type[enum.Enum]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.ty(v)


##


class EnumMode(enum.Enum):
    NAME = 'name'
    VALUE = 'value'


@dc.dataclass(frozen=True)
class EnumMarshalerFactory(MarshalerFactory):
    mode: EnumMode = EnumMode.NAME

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, enum.Enum)):
            return None
        cls: ta.Any = {
            EnumMode.NAME: EnumNameMarshaler,
            EnumMode.VALUE: EnumValueMarshaler,
        }[self.mode]
        return lambda: cls(rty)


@dc.dataclass(frozen=True)
class EnumUnmarshalerFactory(UnmarshalerFactory):
    mode: EnumMode = EnumMode.NAME

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, enum.Enum)):
            return None
        cls: ta.Any = {
            EnumMode.NAME: EnumNameUnmarshaler,
            EnumMode.VALUE: EnumValueUnmarshaler,
        }[self.mode]
        return lambda: cls(rty)
