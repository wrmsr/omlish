import abc
import contextlib
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .bindings import Binding
from .elements import Element
from .injector import AsyncInjector
from .keys import Key
from .keys import as_key
from .providers import Provider
from .types import Scope


if ta.TYPE_CHECKING:
    from . import injector as _injector
    from . import maysync as _maysync
    from . import sync as _sync
else:
    _injector = lang.proxy_import('.injector', __package__)
    _maysync = lang.proxy_import('.maysync', __package__)
    _sync = lang.proxy_import('.sync', __package__)


##


SCOPE_ALIASES: dict[str, Scope] = {}


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class ScopeBinding(Element, lang.Final):
    scope: Scope = dc.xfield(coerce=check.of_isinstance(Scope))


def bind_scope(sc: Scope) -> Element:
    return ScopeBinding(sc)


##


class Singleton(Scope, lang.Singleton, lang.Final):
    pass


SCOPE_ALIASES['singleton'] = Singleton()


##


class ThreadScope(Scope, lang.Singleton, lang.Final):
    pass


SCOPE_ALIASES['thread'] = ThreadScope()


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class SeededScope(Scope, lang.Final):
    tag: ta.Any = dc.xfield(coerce=check.not_none)

    class Manager(lang.Abstract):
        @abc.abstractmethod
        def __call__(self, seeds: ta.Mapping[Key, ta.Any]) -> ta.AsyncContextManager[None]:
            raise NotImplementedError


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class ScopeSeededProvider(Provider):
    ss: SeededScope = dc.xfield(coerce=check.of_isinstance(SeededScope))
    key: Key = dc.xfield(coerce=check.of_isinstance(Key))


def bind_scope_seed(k: ta.Any, ss: SeededScope) -> Element:
    k = as_key(k)
    return Binding(k, ScopeSeededProvider(ss, k))


##


@contextlib.asynccontextmanager
async def async_enter_seeded_scope(
        i: '_injector.AsyncInjector',
        ss: SeededScope,
        keys: ta.Mapping[Key, ta.Any],
) -> ta.AsyncGenerator[None]:
    async with (await i.provide(Key(SeededScope.Manager, tag=ss)))(keys):
        yield


def enter_seeded_scope(
        i: '_sync.Injector',
        ss: SeededScope,
        keys: ta.Mapping[Key, ta.Any],
) -> ta.ContextManager[None]:
    return lang.run_maysync_context_manager(async_enter_seeded_scope(
        i[AsyncInjector],
        ss,
        keys,
    ))


def maysync_enter_seeded_scope(
        i: '_maysync.MaysyncInjector',
        ss: SeededScope,
        keys: ta.Mapping[Key, ta.Any],
) -> ta.ContextManager[None]:
    return lang.sync_async_with(async_enter_seeded_scope(
        i[AsyncInjector],
        ss,
        keys,
    ))
