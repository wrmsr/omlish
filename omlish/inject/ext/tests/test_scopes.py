"""
TODO:
 - ** orthogonal to private ** - so this probably isn't a child injector?
 - nesting?
 - scope-eagers
 - in_(request_scope, ...)
"""
import typing as ta

import pytest  # noqa

from .... import dataclasses as dc
from ...bindings import as_
from ...bindings import as_key
from ...bindings import bind
from ...injector import create_injector
from ...keys import multi
from ...providers import SingletonProvider
from ...providers import as_provider
from ...providers import const
from ...providers import ctor
from ...types import Binding
from ...types import Bindings
from ...types import Cls
from ...types import Injector
from ...types import Key
from ...types import Provider
from ...types import ProviderFn


class ScopeNotOpenException(Exception):
    pass


class _SimpleScope:
    @dc.dataclass(frozen=True)
    class State:
        seeds: dict[Key, ta.Any]
        provisions: dict[Provider, ta.Any] = dc.field(default_factory=dict)

    def __init__(self) -> None:
        super().__init__()
        self._state: _SimpleScope.State | None = None

    @property
    def state(self) -> ta.Optional['_SimpleScope.State']:
        return self._state

    def must_state(self) -> '_SimpleScope.State':
        if (st := self._state) is None:
            raise ScopeNotOpenException()
        return st


_SIMPLE_SCOPE_KEY = Key(_SimpleScope)


@dc.dataclass(frozen=True)
class _Seed:
    key: Key


_SEED_MULTI_KEY = multi(_Seed)


@dc.dataclass(frozen=True, eq=False)
class SimpleScopedProvider(Provider):
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.p.provided_cls(rec)

    def required_keys(self) -> frozenset[Key | None]:
        return frozenset([*self.p.required_keys(), _SIMPLE_SCOPE_KEY])

    def children(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provider_fn(self) -> ProviderFn:
        ipfn = self.p.provider_fn()

        def pfn(i: Injector) -> ta.Any:
            st: _SimpleScope.State = i.provide(_SIMPLE_SCOPE_KEY).must_state()
            try:
                return st.provisions[self]
            except KeyError:
                st.provisions[self] = v = ipfn(i)
                return v

        return pfn


def simple_scoped(p: ta.Any) -> Provider:
    return SimpleScopedProvider(as_provider(p))


@dc.dataclass(frozen=True, eq=False)
class SimpleScopeSeedProvider(Provider):
    k: Key

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.k.cls

    def required_keys(self) -> frozenset[Key | None]:
        return frozenset()

    def children(self) -> ta.Iterable[Provider]:
        return ()

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            st: _SimpleScope.State = i.provide(_SIMPLE_SCOPE_KEY).must_state()
            return st.seeds[self.k]

        return pfn


def bind_simple_scope_seeds(*objs: ta.Any) -> Bindings:
    bs = []
    for obj in objs:
        k = as_key(obj)
        bs.extend([
            Binding(_SIMPLE_SCOPE_KEY, SimpleScopeSeedProvider(k)),
            as_(_SEED_MULTI_KEY, const([_Seed(k)]))
        ])
    return bind(*bs)


def bind_simple_scope() -> Binding:
    return Binding(_SIMPLE_SCOPE_KEY, SingletonProvider(ctor(_SimpleScope)))


# @pytest.mark.skip()
def test_scopes():
    i = create_injector(bind(
        simple_scoped(420),
        bind_simple_scope(),
    ))
    assert i[int] == 420
