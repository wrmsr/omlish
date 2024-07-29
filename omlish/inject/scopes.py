import abc
import contextlib
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from .bindings import Binding
from .bindings import as_binding
from .elements import Element
from .keys import Key
from .keys import as_key
from .providers import Provider
from .types import Scope


if ta.TYPE_CHECKING:
    from . import injector as injector_
else:
    injector_ = lang.proxy_import('.injector', __package__)


##


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
class SeededScope(Scope, lang.Final):
    tag: ta.Any = dc.xfield(coerce=check.not_none)

    class Manager(lang.Abstract):
        @abc.abstractmethod
        def __call__(self, seeds: ta.Mapping[Key, ta.Any]) -> ta.ContextManager[None]:
            raise NotImplementedError


@dc.dataclass(frozen=True, eq=False)
class ScopeSeededProvider(Provider):
    ss: SeededScope = dc.xfield(coerce=check.of_isinstance(SeededScope))
    key: Key = dc.xfield(coerce=check.of_isinstance(Key))

    def provided_ty(self) -> rfl.Type | None:
        return self.key.ty


def bind_scope_seed(ss: SeededScope, k: ta.Any) -> Element:
    k = as_key(k)
    return Binding(k, ScopeSeededProvider(ss, k))


@contextlib.contextmanager
def enter_seeded_scope(
        i: injector_.Injector,
        ss: SeededScope,
        keys: ta.Mapping[Key, ta.Any],
) -> ta.Generator[None, None, None]:
    with i.provide(Key(SeededScope.Manager, tag=ss))(keys):
        yield
