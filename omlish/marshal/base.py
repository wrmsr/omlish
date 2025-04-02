"""
TODO:
 - redacted
 - strongly typed MarshalerFactory base class?
 - strongly typed Composite/Cached Marshaler/Unmarshaler factories - footgun
 - streaming? Start/EndObject, etc..
 - lang.Marker - class name, handle type[Foo]
  - can't disambiguate from str - can't coexist in bare union
 - factories being free MatchFns does more harm than good - in practice these are such big guns you want to write a
   class body if only ceremonially

See:
 - https://github.com/python-attrs/cattrs
 - https://github.com/jcrist/msgspec
 - https://github.com/Fatal1ty/mashumaro
 - https://github.com/Kotlin/kotlinx.serialization/blob/master/docs/serializers.md#custom-serializers

cattrs:
 *

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

https://github.com/yukinarit/pyserde
 - datatypes
  - typing.Union
  - typing.NewType for primitive types
  - typing.Any
  - typing.Literal
  - typing.Generic
  - typing.ClassVar
 - dataclasses.InitVar
 - Enum and IntEnum
 - pathlib.Path
 - decimal.Decimal
 - uuid.UUID
 - datetime.date, datetime.time, datetime.datetime
 - ipaddress
 - numpy types
 - Class Attributes
 - Field Attributes
 - Decorators
 - Type Check
 - Union Representation
 - Forward reference
 - PEP563 Postponed Evaluation of Annotations
 - PEP585 Type Hinting Generics In Standard Collections
 - PEP604 Allow writing union types as X | Y
 - PEP681 Data Class Transform
 - Case Conversion
 - Rename
 - Alias
 - Skip (de)serialization (skip, skip_if, skip_if_false, skip_if_default)
 - Custom field (de)serializer
 - Custom class (de)serializer
 - Custom global (de)serializer
 - Flatten
"""
import abc
import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from ..funcs import match as mfs
from .exceptions import UnhandledTypeError
from .factories import RecursiveTypeFactory
from .factories import TypeCacheFactory
from .factories import TypeMapFactory
from .proxy import _Proxy
from .registries import Registry
from .registries import RegistryItem
from .values import Value


##


class Marshaler(lang.Abstract):
    @abc.abstractmethod
    def marshal(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        raise NotImplementedError


class Unmarshaler(lang.Abstract):
    @abc.abstractmethod
    def unmarshal(self, ctx: 'UnmarshalContext', v: Value) -> ta.Any:
        raise NotImplementedError


##


MarshalerMaker: ta.TypeAlias = mfs.MatchFn[['MarshalContext', rfl.Type], Marshaler]
UnmarshalerMaker: ta.TypeAlias = mfs.MatchFn[['UnmarshalContext', rfl.Type], Unmarshaler]


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


@dc.dataclass(frozen=True)
class MarshalerFactory_(MarshalerFactory):  # noqa
    fn: MarshalerMaker

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self.fn


@dc.dataclass(frozen=True)
class UnmarshalerFactory_(UnmarshalerFactory):  # noqa
    fn: UnmarshalerMaker

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self.fn


##


class SimpleMarshalerFactory(
    MarshalerFactory,
    MarshalerMaker,
    lang.Abstract,
):
    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self


class SimpleUnmarshalerFactory(
    UnmarshalerFactory,
    UnmarshalerMaker,
    lang.Abstract,
):
    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self


##


class MarshalerFactoryMatchClass(
    MarshalerFactory,
    mfs.MatchFnClass[['MarshalContext', rfl.Type], Marshaler],
    lang.Abstract,
):
    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self


class UnmarshalerFactoryMatchClass(
    UnmarshalerFactory,
    mfs.MatchFnClass[['UnmarshalContext', rfl.Type], Unmarshaler],
    lang.Abstract,
):
    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self


##


class MultiMarshalerFactory(MarshalerFactory):
    def __init__(
            self,
            fs: ta.Iterable[MarshalerFactory],
            *,
            strict: bool = False,
    ) -> None:
        super().__init__()

        self._fs = list(fs)
        self._mmf: mfs.MultiMatchFn[[MarshalContext, rfl.Type], Marshaler] = mfs.MultiMatchFn(
            [f.make_marshaler for f in self._fs],
            strict=strict,
        )

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self._mmf


class MultiUnmarshalerFactory(UnmarshalerFactory):
    def __init__(
            self,
            fs: ta.Iterable[UnmarshalerFactory],
            *,
            strict: bool = False,
    ) -> None:
        super().__init__()

        self._fs = list(fs)
        self._mmf: mfs.MultiMatchFn[[UnmarshalContext, rfl.Type], Unmarshaler] = mfs.MultiMatchFn(
            [f.make_unmarshaler for f in self._fs],
            strict=strict,
        )

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self._mmf


##


@dc.dataclass(frozen=True)
class TypeMapMarshalerFactory(
    TypeMapFactory['MarshalContext', Marshaler],
    MarshalerFactory,
):
    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self


@dc.dataclass(frozen=True)
class TypeMapUnmarshalerFactory(
    TypeMapFactory['UnmarshalContext', Unmarshaler],
    UnmarshalerFactory,
):
    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self


# class TypeMapMarshalerFactory(MarshalerFactory):
#     def __init__(self, m: ta.Mapping[rfl.Type, MarshalerFactory]) -> None:
#         super().__init__()
#
#         self._m = m
#         self._tmf: TypeMapFactory['MarshalContext', Marshaler] = TypeMapFactory({
#             t: f.make_marshaler
#             for t, f in m.items()
#         })
#
#     @property
#     def make_marshaler(self) -> MarshalerMaker:
#         return self._tmf


# class TypeMapUnmarshalerFactory(UnmarshalerFactory):
#     def __init__(self, m: ta.Mapping[rfl.Type, UnmarshalerFactory]) -> None:
#         super().__init__()
#
#         self._m = m
#         self._tmf: TypeMapFactory[UnmarshalContext, Unmarshaler] = TypeMapFactory({
#             t: f.make_unmarshaler
#             for t, f in m.items()
#         })
#
#     @property
#     def make_unmarshaler(self) -> UnmarshalerMaker:
#         return self._tmf


##


class TypeCacheMarshalerFactory(MarshalerFactory):
    def __init__(self, f: MarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._tcf: TypeCacheFactory[MarshalContext, Marshaler] = TypeCacheFactory(f.make_marshaler)

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self._tcf


class TypeCacheUnmarshalerFactory(UnmarshalerFactory):
    def __init__(self, f: UnmarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._tcf: TypeCacheFactory[UnmarshalContext, Unmarshaler] = TypeCacheFactory(f.make_unmarshaler)

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self._tcf


##


@dc.dataclass(frozen=True)
class FuncMarshaler(Marshaler, lang.Final):
    fn: ta.Callable[['MarshalContext', ta.Any], Value]

    def marshal(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        return self.fn(ctx, o)


@dc.dataclass(frozen=True)
class FuncUnmarshaler(Unmarshaler, lang.Final):
    fn: ta.Callable[['UnmarshalContext', Value], ta.Any]

    def unmarshal(self, ctx: 'UnmarshalContext', v: Value) -> ta.Any:
        return self.fn(ctx, v)


##


class Option:
    pass


##


@dc.dataclass(frozen=True)
class BaseContext(lang.Abstract):
    registry: Registry
    options: col.TypeMap[Option] = col.TypeMap()

    def _reflect(self, o: ta.Any) -> rfl.Type:
        def override(o):
            if (ovr := self.registry.get_of(o, ReflectOverride)):
                return ovr[-1].rty
            return None

        return rfl.Reflector(override=override).type(o)


@dc.dataclass(frozen=True)
class MarshalContext(BaseContext, lang.Final):
    factory: MarshalerFactory | None = None

    def make(self, o: ta.Any) -> Marshaler:
        rty = self._reflect(o)
        try:
            return check.not_none(self.factory).make_marshaler(self, rty)
        except mfs.MatchGuardError:
            raise UnhandledTypeError(rty)  # noqa


@dc.dataclass(frozen=True)
class UnmarshalContext(BaseContext, lang.Final):
    factory: UnmarshalerFactory | None = None

    def make(self, o: ta.Any) -> Unmarshaler:
        rty = self._reflect(o)
        try:
            return check.not_none(self.factory).make_unmarshaler(self, rty)
        except mfs.MatchGuardError:
            raise UnhandledTypeError(rty)  # noqa


##


class _ProxyMarshaler(_Proxy[Marshaler], Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return self._obj.marshal(ctx, o)


class RecursiveMarshalerFactory(MarshalerFactory, lang.Final):
    def __init__(self, f: MarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._rtf: RecursiveTypeFactory[MarshalContext, Marshaler] = RecursiveTypeFactory(
            self._f.make_marshaler,  # noqa
            _ProxyMarshaler._new,  # noqa
        )

    @property
    def make_marshaler(self) -> MarshalerMaker:
        return self._rtf


class _ProxyUnmarshaler(_Proxy[Unmarshaler], Unmarshaler):
    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self._obj.unmarshal(ctx, v)


class RecursiveUnmarshalerFactory(UnmarshalerFactory, lang.Final):
    def __init__(self, f: UnmarshalerFactory) -> None:
        super().__init__()

        self._f = f
        self._rtf: RecursiveTypeFactory[UnmarshalContext, Unmarshaler] = RecursiveTypeFactory(
            self._f.make_unmarshaler,  # noqa
            _ProxyUnmarshaler._new,  # noqa
        )

    @property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return self._rtf


##


@dc.dataclass(frozen=True, kw_only=True)
class Override(RegistryItem, lang.Final):
    marshaler: Marshaler | None = dc.xfield(None, check_type=(Marshaler, None))
    marshaler_factory: MarshalerFactory | None = None

    unmarshaler: Unmarshaler | None = dc.xfield(None, check_type=(Unmarshaler, None))
    unmarshaler_factory: UnmarshalerFactory | None = None


@dc.dataclass(frozen=True)
class ReflectOverride(RegistryItem, lang.Final):
    rty: rfl.Type
