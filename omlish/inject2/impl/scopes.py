import abc
import threading
import typing as ta

from .. import Key, Provider
from ... import check
from ... import dataclasses as dc
from ... import lang
from ..bindings import Binding
from ..bindings import Scope
from ..bindings import Unscoped
from ..elements import Elements
from ..elements import as_elements
from ..injector import Injector
from ..providers import fn
from ..scopes import ScopeSeededProvider
from ..scopes import SeededScope
from ..scopes import Singleton
from ..scopes import Thread
from .bindings import BindingImpl
from .providers import PROVIDER_IMPLS_BY_PROVIDER
from .providers import ProviderImpl


class ScopeImpl(lang.Abstract):
    @property
    @abc.abstractmethod
    def scope(self) -> Scope:
        raise NotImplementedError

    def auto_elements(self) -> Elements | None:
        return None

    @abc.abstractmethod
    def provide(self, binding: BindingImpl, injector: Injector) -> ta.Any:
        raise NotImplementedError


class UnscopedScopeImpl(ScopeImpl, lang.Final):
    @property
    def scope(self) -> Unscoped:
        return Unscoped()

    def provide(self, binding: BindingImpl, injector: Injector) -> ta.Any:
        return binding.provider.provide(injector)


class SingletonScopeImpl(ScopeImpl, lang.Final):
    def __init__(self) -> None:
        super().__init__()
        self._dct: dict[BindingImpl, ta.Any] = {}

    @property
    def scope(self) -> Singleton:
        return Singleton()

    def provide(self, binding: BindingImpl, injector: Injector) -> ta.Any:
        try:
            return self._dct[binding]
        except KeyError:
            pass
        v = binding.provider.provide(injector)
        self._dct[binding] = v
        return v


class ThreadScopeImpl(ScopeImpl, lang.Final):
    def __init__(self) -> None:
        super().__init__()
        self._local = threading.local()

    @property
    def scope(self) -> Thread:
        return Thread()

    def provide(self, binding: BindingImpl, injector: Injector) -> ta.Any:
        dct: dict[BindingImpl, ta.Any]
        try:
            dct = self._local.dct
        except AttributeError:
            dct = self._local.dct = {}
        try:
            return dct[binding]
        except KeyError:
            pass
        v = binding.provider.provide(injector)
        dct[binding] = v
        return v


@dc.dataclass(frozen=True, eq=False)
class ScopeSeededProviderImpl(ProviderImpl):
    p: ScopeSeededProvider

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provide(self, injector: Injector) -> ta.Any:
        raise NotImplementedError


PROVIDER_IMPLS_BY_PROVIDER[ScopeSeededProvider] = ScopeSeededProviderImpl


class SeededScopeImpl(ScopeImpl):
    def __init__(self, ss: SeededScope) -> None:
        super().__init__()
        self._ss = check.isinstance(ss, SeededScope)
        self._st: SeededScopeImpl.State | None = None

    @property
    def scope(self) -> SeededScope:
        return self._ss

    @dc.dataclass(frozen=True)
    class State:
        seeds: dict[Key, ta.Any]
        prvs: dict[BindingImpl, ta.Any] = dc.field(default_factory=dict)

    class Manager(SeededScope.Manager, lang.Final):
        def __init__(self, ss: SeededScope, i: Injector) -> None:
            super().__init__()
            self._ss = ss
            # self._ssi = i.provide(Key(SeededScopeImpl, tag=))
            raise NotImplementedError

        def __enter__(self, seeds: ta.Mapping[Key, ta.Any]) -> None:
            raise NotImplementedError

        def __exit__(self, exc_type, exc_val, exc_tb):
            raise NotImplementedError

    def auto_elements(self) -> Elements:
        return as_elements(
            Binding(Key(SeededScope.Manager, tag=self._ss), fn(lang.typed_partial(SeededScopeImpl.Manager, ss=self._ss)), scope=Singleton()),
        )

    def provide(self, binding: BindingImpl, injector: Injector) -> ta.Any:
        raise NotImplementedError


SCOPE_IMPLS_BY_SCOPE: dict[type[Scope], ta.Callable[..., ScopeImpl]] = {
    Unscoped: lambda _: UnscopedScopeImpl(),
    Singleton: lambda _: SingletonScopeImpl(),
    Thread: lambda _: ThreadScopeImpl(),
    SeededScope: lambda s: SeededScopeImpl(s),
}


def make_scope_impl(s: Scope) -> ScopeImpl:
    try:
        fac = SCOPE_IMPLS_BY_SCOPE[type(s)]
    except KeyError:
        pass
    else:
        return fac(s)

    raise TypeError(s)
