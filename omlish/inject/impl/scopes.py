"""
TODO:
 - ContextVar ('context')
 - greenlet?
 - dynamic? https://github.com/wrmsr/iceworm/blob/2f6b4d5e9d237ef9665f7d57cfa6ce328efa0757/iceworm/utils/inject.py#L44
"""
import abc
import contextlib
import threading
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ..bindings import Binding
from ..elements import Elements
from ..elements import as_elements
from ..exceptions import ScopeAlreadyOpenError
from ..exceptions import ScopeNotOpenError
from ..injector import Injector
from ..keys import Key
from ..providers import FnProvider
from ..providers import Provider
from ..scopes import ScopeSeededProvider
from ..scopes import SeededScope
from ..scopes import Singleton
from ..scopes import ThreadScope
from ..types import Scope
from ..types import Unscoped
from .bindings import BindingImpl
from .providers import PROVIDER_IMPLS_BY_PROVIDER
from .providers import ProviderImpl


if ta.TYPE_CHECKING:
    from . import injector as injector_
else:
    injector_ = lang.proxy_import('.injector', __package__)


##


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
    def scope(self) -> ThreadScope:
        return ThreadScope()

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


##


@dc.dataclass(frozen=True, eq=False)
class ScopeSeededProviderImpl(ProviderImpl):
    p: ScopeSeededProvider

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provide(self, injector: Injector) -> ta.Any:
        ii = check.isinstance(injector, injector_.InjectorImpl)
        ssi = check.isinstance(ii.get_scope_impl(self.p.ss), SeededScopeImpl)
        return ssi.must_state().seeds[self.p.key]


PROVIDER_IMPLS_BY_PROVIDER[ScopeSeededProvider] = ScopeSeededProviderImpl


class SeededScopeImpl(ScopeImpl):
    @dc.dataclass(frozen=True)
    class State:
        seeds: dict[Key, ta.Any]
        prvs: dict[BindingImpl, ta.Any] = dc.field(default_factory=dict)

    def __init__(self, ss: SeededScope) -> None:
        super().__init__()
        self._ss = check.isinstance(ss, SeededScope)
        self._st: SeededScopeImpl.State | None = None

    @property
    def scope(self) -> SeededScope:
        return self._ss

    def must_state(self) -> 'SeededScopeImpl.State':
        if (st := self._st) is None:
            raise ScopeNotOpenError(self._ss)
        return st

    class Manager(SeededScope.Manager, lang.Final):
        def __init__(self, ss: SeededScope, i: Injector) -> None:
            super().__init__()
            self._ss = check.isinstance(ss, SeededScope)
            self._ii = check.isinstance(i, injector_.InjectorImpl)
            self._ssi = check.isinstance(self._ii.get_scope_impl(self._ss), SeededScopeImpl)

        @contextlib.contextmanager
        def __call__(self, seeds: ta.Mapping[Key, ta.Any]) -> ta.Generator[None, None, None]:
            try:
                if self._ssi._st is not None:  # noqa
                    raise ScopeAlreadyOpenError(self._ss)
                self._ssi._st = SeededScopeImpl.State(dict(seeds))  # noqa
                self._ii._instantiate_eagers(self._ss)  # noqa
                yield
            finally:
                if self._ssi._st is None:  # noqa
                    raise ScopeNotOpenError(self._ss)
                self._ssi._st = None  # noqa

    def auto_elements(self) -> Elements:
        return as_elements(
            Binding(
                Key(SeededScope.Manager, tag=self._ss),
                FnProvider(lang.typed_partial(SeededScopeImpl.Manager, ss=self._ss)),
                scope=Singleton(),
            ),
        )

    def provide(self, binding: BindingImpl, injector: Injector) -> ta.Any:
        st = self.must_state()
        try:
            return st.prvs[binding]
        except KeyError:
            pass
        v = binding.provider.provide(injector)
        st.prvs[binding] = v
        return v


##


SCOPE_IMPLS_BY_SCOPE: dict[type[Scope], ta.Callable[..., ScopeImpl]] = {
    Unscoped: lambda _: UnscopedScopeImpl(),
    Singleton: lambda _: SingletonScopeImpl(),
    ThreadScope: lambda _: ThreadScopeImpl(),
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
