import abc
import typing as ta

from ... import lang
from ... import reflect as rfl
from ...funcs import guard as gfs
from .configs import ConfigRegistry
from .contexts import MarshalContext
from .contexts import MarshalFactoryContext
from .contexts import UnmarshalContext
from .contexts import UnmarshalFactoryContext
from .values import Value


T = ta.TypeVar('T')


##


class Marshaler(lang.Abstract):
    @abc.abstractmethod
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        raise NotImplementedError


class Unmarshaler(lang.Abstract):
    @abc.abstractmethod
    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        raise NotImplementedError


##


MarshalerMaker: ta.TypeAlias = gfs.GuardFn[[MarshalFactoryContext, rfl.Type], Marshaler]
UnmarshalerMaker: ta.TypeAlias = gfs.GuardFn[[UnmarshalFactoryContext, rfl.Type], Unmarshaler]


class MarshalerFactory(lang.Abstract):
    @abc.abstractmethod
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        raise NotImplementedError


class UnmarshalerFactory(lang.Abstract):
    @abc.abstractmethod
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        raise NotImplementedError


##


class Marshaling(lang.Abstract):
    @abc.abstractmethod
    def config_registry(self) -> ConfigRegistry:
        raise NotImplementedError

    @abc.abstractmethod
    def marshaler_factory(self) -> MarshalerFactory:
        raise NotImplementedError

    @abc.abstractmethod
    def unmarshaler_factory(self) -> UnmarshalerFactory:
        raise NotImplementedError

    ##

    def new_marshal_factory_context(self) -> MarshalFactoryContext:
        return MarshalFactoryContext(
            configs=self.config_registry(),
            marshaler_factory=self.marshaler_factory(),
        )

    def new_unmarshal_factory_context(self) -> UnmarshalFactoryContext:
        return UnmarshalFactoryContext(
            configs=self.config_registry(),
            unmarshaler_factory=self.unmarshaler_factory(),
        )

    ##

    def new_marshal_context(self) -> MarshalContext:
        return MarshalContext(
            configs=self.config_registry(),
            marshal_factory_context=self.new_marshal_factory_context(),
        )

    def new_unmarshal_context(self) -> UnmarshalContext:
        return UnmarshalContext(
            configs=self.config_registry(),
            unmarshal_factory_context=self.new_unmarshal_factory_context(),
        )

    #

    @ta.final
    def marshal(self, obj: ta.Any, ty: ta.Any | None = None, **kwargs: ta.Any) -> Value:
        return self.new_marshal_context(**kwargs).marshal(obj, ty)

    @ta.overload
    def unmarshal(self, v: Value, ty: type[T], **kwargs: ta.Any) -> T:
        ...

    @ta.overload
    def unmarshal(self, v: Value, ty: ta.Any, **kwargs: ta.Any) -> ta.Any:
        ...

    @ta.final
    def unmarshal(self, v, ty, **kwargs):
        return self.new_unmarshal_context(**kwargs).unmarshal(v, ty)


##


# MarshalerOrUnmarshaler: ta.TypeAlias = Marshaler | Unmarshaler
# MarshalerOrUnmarshalerT = ta.TypeVar('MarshalerOrUnmarshalerT', bound=MarshalerOrUnmarshaler)
#
# MarshalContextOrUnmarshalContext: ta.TypeAlias = MarshalContext | UnmarshalContext
# MarshalContextOrUnmarshalContextT = ta.TypeVar('MarshalContextOrUnmarshalContextT', bound=MarshalContextOrUnmarshalContext)  # noqa
#
# MarshalerMakerOrUnmarshalerMaker: ta.TypeAlias = MarshalerMaker | UnmarshalerMaker
