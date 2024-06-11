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
from ...bindings import bind
from ...injector import create_injector
from ...providers import SingletonProvider
from ...providers import as_provider
from ...providers import ctor
from ...types import Binding
from ...types import Cls
from ...types import Injector
from ...types import Key
from ...types import Provider
from ...types import ProviderFn


class _SimpleScope:
    provisions: dict[Key, ta.Any]


_SIMPLE_SCOPE_KEY = Key(_SimpleScope)


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
        def pfn(i: Injector) -> ta.Any:
            raise NotImplementedError

        ufn = self.p.provider_fn()
        return pfn


def simple_scoped(p: ta.Any) -> Provider:
    return SimpleScopedProvider(as_provider(p))


def bind_simple_scope() -> Binding:
    return Binding(_SIMPLE_SCOPE_KEY, SingletonProvider(ctor(_SimpleScope)))


# @pytest.mark.skip()
def test_scopes():
    i = create_injector(bind(
        simple_scoped(420),
        bind_simple_scope(),
    ))
    assert i[int] == 420
