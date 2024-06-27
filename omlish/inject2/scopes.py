import abc
import typing as ta

from . import Cls
from .. import check
from .. import dataclasses as dc
from .. import lang
from .bindings import Binding
from .bindings import Scope
from .bindings import as_binding
from .elements import Element
from .keys import Key
from .providers import Provider


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ScopeBinding(Element, lang.Final):
    scope: Scope = dc.xfield(coerce=check.of_isinstance(Scope))


def bind_scope(sc: Scope) -> Element:
    return ScopeBinding(sc)


def in_(b: ta.Any, sc: Scope) -> 'Binding':
    return dc.replace(as_binding(b), scope=check.isinstance(sc, Scope))


class Singleton(Scope, lang.Singleton, lang.Final):
    pass


def singleton(b: ta.Any) -> 'Binding':
    return in_(b, Singleton())


class Thread(Scope, lang.Singleton, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ScopeSeed(Element, lang.Final):
    key: Key


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class SeededScope(Scope, lang.Final):
    tag: ta.Any = dc.xfield(coerce=check.not_none)

    class Manager(lang.Abstract):
        @abc.abstractmethod
        def __enter__(self, seeds: ta.Mapping[Key, ta.Any]) -> None:
            raise NotImplementedError

        @abc.abstractmethod
        def __exit__(self, exc_type, exc_val, exc_tb):
            raise NotImplementedError


@dc.dataclass(frozen=True, eq=False)
class ScopeSeededProvider(Provider):
    def provided_cls(self) -> Cls | None:
        raise NotImplementedError
