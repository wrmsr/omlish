"""
TODO:
 - ** orthogonal to private ** - so this probably isn't a child injector?
 - nesting?
 - scope-eagers
 - in_(request_scope, ...)
"""
import typing as ta

import pytest  # noqa

from ... import cached
from ... import check
from ... import dataclasses as dc
from ... import lang
from ..bindings import as_
from ..bindings import as_key
from ..bindings import bind
from ..keys import multi
from ..providers import SingletonProvider
from ..providers import as_provider
from ..providers import const
from ..types import Binding
from ..types import Bindings
from ..types import Cls
from ..types import Injector
from ..types import Key
from ..types import Provider
from ..types import ProviderFn


class ScopeAlreadyOpenException(Exception):
    pass


class ScopeNotOpenException(Exception):
    pass


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ScopeTag(lang.Final):
    tag: ta.Any

    @cached.property
    def _scope_key(self) -> Key:
        return Key(_Scope, tag=self)

    @cached.property
    def _seed_key(self) -> Key:
        return Key(_Seed, tag=self, multi=True)


class _Scope(lang.Final):
    @dc.dataclass(frozen=True)
    class State:
        seeds: dict[Key, ta.Any]
        provisions: dict[Provider, ta.Any] = dc.field(default_factory=dict)

    def __init__(self, tag: ScopeTag) -> None:
        super().__init__()
        self._tag = check.isinstance(tag, ScopeTag)
        self._state: _Scope.State | None = None

    @property
    def tag(self) -> ScopeTag:
        return self._tag

    @property
    def state(self) -> ta.Optional['_Scope.State']:
        return self._state

    def must_state(self) -> '_Scope.State':
        if (st := self._state) is None:
            raise ScopeNotOpenException()
        return st

    def open(self, seeds: ta.Mapping[Key, ta.Any]) -> None:
        if self._state is not None:
            raise ScopeAlreadyOpenException()
        self._state = _Scope.State(dict(seeds))

    def close(self) -> None:
        self._state = None


_SIMPLE_SCOPE_KEY = Key(_Scope)


@dc.dataclass(frozen=True)
class _Seed:
    key: Key


_SEED_MULTI_KEY = multi(_Seed)


@dc.dataclass(frozen=True, eq=False)
class ScopedProvider(Provider):
    tag: ScopeTag
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.p.provided_cls(rec)

    def required_keys(self) -> frozenset[Key | None]:
        return frozenset([*self.p.required_keys(), self.tag._scope_key])  # noqa

    def children(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provider_fn(self) -> ProviderFn:
        ipfn = self.p.provider_fn()

        def pfn(i: Injector) -> ta.Any:
            st: _Scope.State = i.provide(self.tag._scope_key).must_state()  # noqa
            try:
                return st.provisions[self]
            except KeyError:
                st.provisions[self] = v = ipfn(i)
                return v

        return pfn


def scoped(tag: ScopeTag, p: ta.Any) -> Provider:
    return ScopedProvider(check.isinstance(tag, ScopeTag), as_provider(p))


@dc.dataclass(frozen=True, eq=False)
class ScopeSeedProvider(Provider):
    tag: ScopeTag
    k: Key

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.k.cls

    def required_keys(self) -> frozenset[Key | None]:
        return frozenset([self.tag._scope_key])  # noqa

    def children(self) -> ta.Iterable[Provider]:
        return ()

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            st: _Scope.State = i.provide(self.tag._scope_key).must_state()  # noqa
            return st.seeds[self.k]

        return pfn


def bind_scope_seeds(tag: ScopeTag, *objs: ta.Any) -> Bindings:
    check.isinstance(tag, ScopeTag)
    bs = []
    for obj in objs:
        k = as_key(obj)
        bs.extend([
            Binding(k, ScopeSeedProvider(tag, k)),  # noqa
            as_(tag._seed_key, const([_Seed(k)]))  # noqa
        ])
    return bind(*bs)


def bind_scope(tag: ScopeTag) -> Binding:
    check.isinstance(tag, ScopeTag)
    return Binding(tag._scope_key, SingletonProvider(const(_Scope(tag))))  # noqa
