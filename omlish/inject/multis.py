"""
TODO:
 - DynamicSetBinding / DynamicMapBinding ? provider of set[T] / map[K, V] ?
  - doable not guicey - too much dynamism
 - scopes
"""
import collections.abc
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from .bindings import Binding
from .elements import Element
from .elements import ElementGenerator
from .keys import Key
from .keys import as_key
from .providers import Provider


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


def is_set_multi_key(mk: Key) -> bool:
    return rfl.get_concrete_type(mk.ty) is collections.abc.Set


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class SetBinding(Element, lang.Final):
    multi_key: Key = dc.xfield(validate=is_set_multi_key)
    dst: Key = dc.xfield(coerce=check.of_isinstance(Key))


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class SetProvider(Provider):
    multi_key: Key = dc.xfield(validate=is_set_multi_key)


#


def is_map_multi_key(mk: Key) -> bool:
    return rfl.get_concrete_type(mk.ty) is collections.abc.Mapping


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class MapBinding(Element, lang.Final):
    multi_key: Key = dc.xfield(validate=is_map_multi_key)
    map_key: ta.Any = dc.xfield()
    dst: Key = dc.xfield(coerce=check.of_isinstance(Key))


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class MapProvider(Provider):
    multi_key: Key = dc.xfield(validate=is_map_multi_key)


##


class SetBinder(ElementGenerator, ta.Generic[T]):
    def __init__(self, *, tag: ta.Any = None) -> None:
        super().__init__()

        self._tag: ta.Any = tag
        self._sbs: list[SetBinding] = []

    @lang.cached_property
    def _multi_key(self) -> Key:
        oty = rfl.type_(rfl.get_orig_class(self))
        ety = check.single(check.isinstance(oty, rfl.Generic).args)
        return Key(ta.AbstractSet[ety], tag=self._tag)  # type: ignore

    @lang.cached_property
    def _set_provider_binding(self) -> Element:
        return Binding(self._multi_key, SetProvider(self._multi_key))

    def bind(self, *keys: ta.Any) -> ta.Self:
        if not isinstance(self, SetBinder):
            raise TypeError
        self._sbs.extend(SetBinding(self._multi_key, as_key(k)) for k in keys)
        return self

    def __iter__(self) -> ta.Iterator[Element]:
        yield self._set_provider_binding
        yield from self._sbs


set_binder = SetBinder


#


class MapBinder(ElementGenerator, ta.Generic[K, V]):
    def __init__(self, *, tag: ta.Any = None) -> None:
        super().__init__()

        self._tag: ta.Any = tag
        self._mbs: list[MapBinding] = []

    @lang.cached_property
    def _multi_key(self) -> Key:
        oty = rfl.type_(rfl.get_orig_class(self))
        kty, vty = check.isinstance(oty, rfl.Generic).args
        return Key(ta.Mapping[kty, vty], tag=self._tag)  # type: ignore

    @lang.cached_property
    def _map_provider_binding(self) -> Element:
        return Binding(self._multi_key, MapProvider(self._multi_key))

    def bind(self, map_key: K, map_value_key: ta.Any) -> ta.Self:
        if not isinstance(self, MapBinder):
            raise TypeError
        self._mbs.append(MapBinding(self._multi_key, map_key, as_key(map_value_key)))
        return self

    def __iter__(self) -> ta.Iterator[Element]:
        yield self._map_provider_binding
        yield from self._mbs


map_binder = MapBinder
