import dataclasses as dc
import enum
import typing as ta

from ... import check
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from ..base.values import Value


##


@dc.dataclass(frozen=True)
class EnumMarshaler(Marshaler):
    ty: type[enum.Enum]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return o.name


class EnumMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, enum.Enum)):
            return None
        return lambda: EnumMarshaler(rty)  # noqa


@dc.dataclass(frozen=True)
class EnumUnmarshaler(Unmarshaler):
    ty: type[enum.Enum]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.ty[check.isinstance(v, str)]


class EnumUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, enum.Enum)):
            return None
        return lambda: EnumUnmarshaler(rty)  # noqa
