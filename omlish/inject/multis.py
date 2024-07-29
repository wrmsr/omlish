"""
TODO:
 - scopes
 - checks (enforce AbstractSet / Mapping)
 - Cls -> rfl
"""
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .bindings import Binding
from .elements import Element
from .keys import Key
from .keys import as_key
from .providers import Provider
from .types import Cls


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class SetBinding(Element, lang.Final):
    multi_key: Key  # ta.AbstractSet
    dst: Key


@dc.dataclass(frozen=True, eq=False)
class SetProvider(Provider):
    multi_key: Key  # ta.AbstractSet

    def provided_cls(self) -> Cls | None:
        return self.multi_key.cls


def bind_set_provider(multi_key: ta.Any) -> Element:
    # multi_key = as_key(multi_key)  # ta.AbstractSet
    return Binding(multi_key, SetProvider(multi_key))


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class MapBinding(Element, lang.Final):
    multi_key: Key  # ta.Mapping
    map_key: ta.Any
    dst: Key


@dc.dataclass(frozen=True, eq=False)
class MapProvider(Provider):
    multi_key: Key  # ta.Mapping

    def provided_cls(self) -> Cls | None:
        return self.multi_key.cls


def bind_map_provider(multi_key: ta.Any) -> Element:
    # multi_key = as_key(multi_key)  # ta.Mapping
    return Binding(multi_key, MapProvider(multi_key))
