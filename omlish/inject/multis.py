"""
TODO:
 - scopes
"""
import collections.abc
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from .bindings import Binding
from .elements import Element
from .keys import Key
from .keys import as_key
from .providers import Provider


##


def _check_set_multi_key(mk: Key) -> bool:
    return rfl.get_concrete_type(mk.ty) is collections.abc.Set


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class SetBinding(Element, lang.Final):
    multi_key: Key = dc.xfield(check=_check_set_multi_key)
    dst: Key = dc.xfield()


@dc.dataclass(frozen=True, eq=False)
class SetProvider(Provider):
    multi_key: Key = dc.xfield(check=_check_set_multi_key)

    def provided_ty(self) -> rfl.Type | None:
        return self.multi_key.ty


def bind_set_provider(multi_key: ta.Any) -> Element:
    multi_key = as_key(multi_key)
    return Binding(multi_key, SetProvider(multi_key))


##


def _check_map_multi_key(mk: Key) -> bool:
    return rfl.get_concrete_type(mk.ty) is collections.abc.Mapping


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class MapBinding(Element, lang.Final):
    multi_key: Key = dc.xfield(check=_check_map_multi_key)
    map_key: ta.Any = dc.xfield(())
    dst: Key = dc.xfield(())


@dc.dataclass(frozen=True, eq=False)
class MapProvider(Provider):
    multi_key: Key = dc.xfield(check=_check_map_multi_key)

    def provided_ty(self) -> rfl.Type | None:
        return self.multi_key.ty


def bind_map_provider(multi_key: ta.Any) -> Element:
    multi_key = as_key(multi_key)
    return Binding(multi_key, MapProvider(multi_key))
