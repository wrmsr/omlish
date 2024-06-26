import abc
import threading
import typing as ta

from ... import check
from ... import lang
from ..injector import Injector
from ..scopes import Scope
from ..scopes import SeededScope
from ..scopes import Singleton
from ..scopes import Thread
from ..scopes import Unscoped
from .bindings import BindingImpl


class ScopeImpl(lang.Abstract):
    @property
    @abc.abstractmethod
    def scope(self) -> Scope:
        raise NotImplementedError

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


class SeededScopeImpl(ScopeImpl):
    def __init__(self, ss: SeededScope) -> None:
        super().__init__()
        self._ss = check.isinstance(ss, SeededScope)

    @property
    def scope(self) -> SeededScope:
        return self._ss

    def provide(self, binding: BindingImpl, injector: Injector) -> ta.Any:
        raise NotImplementedError


SCOPE_IMPLS_BY_SCOPE: dict[type[Scope], ta.Callable[..., ScopeImpl]] = {
    Unscoped: lambda _: UnscopedScopeImpl(),
    Singleton: lambda _: SingletonScopeImpl(),
    Thread: lambda _: ThreadScopeImpl(),
    SeededScope: lambda s: SeededScopeImpl(s),
}


def make_scope_impl(p: Scope) -> ScopeImpl:
    try:
        fac = SCOPE_IMPLS_BY_SCOPE[type(p)]
    except KeyError:
        pass
    else:
        return fac(p)

    raise TypeError(p)
