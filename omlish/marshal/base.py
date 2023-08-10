"""
TODO:
 - mappings
 - redacted
 - strongly typed Composite/Cached Marshaler/Unmarshaler factories - footgun
 - streaming? Start/EndObject, etc..

Jackson:
 - USE_ANNOTATIONS
 - AUTO_DETECT_CREATORS
 - AUTO_DETECT_FIELDS
 - AUTO_DETECT_GETTERS
 - AUTO_DETECT_IS_GETTERS
 - AUTO_DETECT_SETTERS
 - REQUIRE_SETTERS_FOR_GETTERS
 - USE_GETTERS_AS_SETTERS
 - INFER_CREATOR_FROM_CONSTRUCTOR_PROPERTIES
 - INFER_PROPERTY_MUTATORS
 - ALLOW_FINAL_FIELDS_AS_MUTATORS
 - ALLOW_VOID_VALUED_PROPERTIES
 - CAN_OVERRIDE_ACCESS_MODIFIERS
 - OVERRIDE_PUBLIC_ACCESS_MODIFIERS
 - SORT_PROPERTIES_ALPHABETICALLY
 - USE_WRAPPER_NAME_AS_PROPERTY_NAME
 - ACCEPT_CASE_INSENSITIVE_ENUMS
 - ACCEPT_CASE_INSENSITIVE_PROPERTIES
 - ACCEPT_CASE_INSENSITIVE_VALUES
 - ALLOW_EXPLICIT_PROPERTY_RENAMING
 - USE_STD_BEAN_NAMING
 - ALLOW_COERCION_OF_SCALARS
 - DEFAULT_VIEW_INCLUSION
 - IGNORE_DUPLICATE_MODULE_REGISTRATIONS
 - IGNORE_MERGE_FOR_UNMERGEABLE
 - USE_BASE_TYPE_AS_DEFAULT_IMPL
 - USE_STATIC_TYPING
 - BLOCK_UNSAFE_POLYMORPHIC_BASE_TYPES
"""
import abc
import dataclasses as dc
import typing as ta

from .. import check
from .. import reflect as rfl
from .exceptions import UnhandledTypeException
from .factories import Factory
from .factories import RecursiveTypeFactory
from .registries import Registry
from .registries import RegistryItem
from .utils import _Proxy
from .values import Value


##


class Marshaler(abc.ABC):
    @abc.abstractmethod
    def marshal(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        raise NotImplementedError


class Unmarshaler(abc.ABC):
    @abc.abstractmethod
    def unmarshal(self, ctx: 'UnmarshalContext', v: Value) -> ta.Any:
        raise NotImplementedError


MarshalerFactory = Factory[Marshaler, 'MarshalContext', rfl.Reflected]
UnmarshalerFactory = Factory[Unmarshaler, 'UnmarshalContext', rfl.Reflected]


##


@dc.dataclass(frozen=True)
class FuncMarshaler(Marshaler):
    fn: ta.Callable[['MarshalContext', ta.Any], Value]

    def marshal(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        return self.fn(ctx, o)


@dc.dataclass(frozen=True)
class FuncUnmarshaler(Unmarshaler):
    fn: ta.Callable[['UnmarshalContext', Value], ta.Any]

    def unmarshal(self, ctx: 'UnmarshalContext', v: Value) -> ta.Any:
        return self.fn(ctx, v)


##


@dc.dataclass(frozen=True)
class BaseContext(abc.ABC):
    registry: Registry


@dc.dataclass(frozen=True)
class MarshalContext(BaseContext):
    factory: ta.Optional[MarshalerFactory] = None

    def make(self, o: ta.Any) -> Marshaler:
        rty = rfl.reflect(o)
        if (m := check.not_none(self.factory)(self, rty)) is not None:  # noqa
            return m
        raise UnhandledTypeException(rty)


@dc.dataclass(frozen=True)
class UnmarshalContext(BaseContext):
    factory: ta.Optional[UnmarshalerFactory] = None

    def make(self, o: ta.Any) -> Unmarshaler:
        rty = rfl.reflect(o)
        if (m := check.not_none(self.factory)(self, rty)) is not None:  # noqa
            return m
        raise UnhandledTypeException(rty)


##


class _ProxyMarshaler(_Proxy[Marshaler], Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return self._obj.marshal(ctx, o)


class RecursiveMarshalerFactory(RecursiveTypeFactory[Marshaler, MarshalContext]):
    def __init__(self, f: MarshalerFactory) -> None:
        super().__init__(f, _ProxyMarshaler._new)  # noqa


class _ProxyUnmarshaler(_Proxy[Unmarshaler], Unmarshaler):
    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self._obj.unmarshal(ctx, v)


class RecursiveUnmarshalerFactory(RecursiveTypeFactory[Unmarshaler, UnmarshalContext]):
    def __init__(self, f: UnmarshalerFactory) -> None:
        super().__init__(f, _ProxyUnmarshaler._new)  # noqa


##


@dc.dataclass(frozen=True)
class SetType(RegistryItem):
    marshaler: ta.Optional[Marshaler] = None
    marshaler_factory: ta.Optional[MarshalerFactory] = None

    unmarshaler: ta.Optional[Unmarshaler] = None
    unmarshaler_factory: ta.Optional[UnmarshalerFactory] = None
