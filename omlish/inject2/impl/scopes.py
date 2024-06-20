import abc
import typing as ta

from ... import lang
from ..injector import Injector
from ..scopes import Scope
from ..scopes import Singleton
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


class UnscopedImpl(ScopeImpl, lang.Final):
    @property
    def scope(self) -> Scope:
        return Unscoped()

    def provide(self, binding: BindingImpl, injector: Injector) -> ta.Any:
        return binding.provider.provide(injector)


class SingletonImpl(ScopeImpl, lang.Final):
    def __init__(self) -> None:
        super().__init__()
        self._dct: dict[BindingImpl, ta.Any] = {}

    @property
    def scope(self) -> Scope:
        return Singleton()

    def provide(self, binding: BindingImpl, injector: Injector) -> ta.Any:
        try:
            return self._dct[binding]
        except KeyError:
            pass
        v = binding.provider.provide(injector)
        self._dct[binding] = v
        return v
