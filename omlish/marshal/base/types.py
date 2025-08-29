import abc
import typing as ta

from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
from .configs import ConfigRegistry
from .contexts import MarshalContext
from .contexts import UnmarshalContext
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


MarshalerMaker: ta.TypeAlias = mfs.MatchFn[[MarshalContext, rfl.Type], Marshaler]
UnmarshalerMaker: ta.TypeAlias = mfs.MatchFn[[UnmarshalContext, rfl.Type], Unmarshaler]


class MarshalerFactory(lang.Abstract):
    @property
    @abc.abstractmethod
    def make_marshaler(self) -> MarshalerMaker:
        raise NotImplementedError


class UnmarshalerFactory(lang.Abstract):
    @property
    @abc.abstractmethod
    def make_unmarshaler(self) -> UnmarshalerMaker:
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

    #

    def new_marshal_context(self, **kwargs: ta.Any) -> MarshalContext:
        return MarshalContext(
            config_registry=self.config_registry(),
            factory=self.marshaler_factory(),
            **kwargs,
        )

    def new_unmarshal_context(self, **kwargs: ta.Any) -> UnmarshalContext:
        return UnmarshalContext(
            config_registry=self.config_registry(),
            factory=self.unmarshaler_factory(),
            **kwargs,
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
