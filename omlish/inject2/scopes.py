import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .keys import Key

if ta.TYPE_CHECKING:
    from . import bindings as bindings_
else:
    bindings_ = lang.proxy_import('.bindings', __package__)


class Scope(lang.Abstract):
    def __repr__(self) -> str:
        return type(self).__name__


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ScopeBinding(Element, lang.Final):
    scope: Scope = dc.xfield(coerce=check.of_isinstance(Scope))


def bind_scope(sc: Scope) -> Element:
    return ScopeBinding(sc)


def in_(b: ta.Any, sc: Scope) -> 'bindings_.Binding':
    return dc.replace(bindings_.as_binding(b), scope=check.isinstance(sc, Scope))


class Unscoped(Scope, lang.Singleton, lang.Final):
    pass


class Singleton(Scope, lang.Singleton, lang.Final):
    pass


def singleton(b: ta.Any) -> 'bindings_.Binding':
    return in_(b, Singleton())


class Thread(Scope, lang.Singleton, lang.Final):
    pass


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ScopeSeed(Element, lang.Final):
    key: Key


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class SeededScope(Scope, lang.Final):
    tag: ta.Any = dc.xfield(coerce=check.not_none)
