import abc
import typing as ta

from ... import collections as col
from ... import lang
from ... import reflect as rfl
from ...funcs import guard as gfs
from .configs import ConfigRegistry
from .contexts import MarshalContext
from .contexts import MarshalFactoryContext
from .contexts import UnmarshalContext
from .contexts import UnmarshalFactoryContext
from .options import Option
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

    def new_marshal_context(self, options: ta.Iterable[Option] | None = None) -> MarshalContext:
        return MarshalContext(
            marshal_factory_context=self.new_marshal_factory_context(),
            options=col.TypeMap.of(options or ()),
        )

    def new_unmarshal_context(self, options: ta.Iterable[Option] | None = None) -> UnmarshalContext:
        return UnmarshalContext(
            unmarshal_factory_context=self.new_unmarshal_factory_context(),
            options=col.TypeMap.of(options or ()),
        )

    #

    @ta.final
    def marshal(
            self,
            obj: ta.Any,
            ty: ta.Any | None = None,
            *options: Option,
    ) -> Value:
        return self.new_marshal_context(options).marshal(obj, ty)

    @ta.overload
    def unmarshal(
            self,
            v: Value,
            ty: type[T],
            *options: Option,
    ) -> T:
        ...

    @ta.overload
    def unmarshal(
            self,
            v: Value,
            ty: ta.Any,
            *options: Option,
    ) -> ta.Any:
        ...

    @ta.final
    def unmarshal(self, v, ty, *options):
        return self.new_unmarshal_context(options).unmarshal(v, ty)
