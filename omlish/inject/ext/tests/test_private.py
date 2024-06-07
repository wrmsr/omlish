import itertools
import typing as ta

import pytest  # noqa

from .... import check
from .... import lang
from .... import dataclasses as dc
from ...bindings import as_
from ...bindings import as_key
from ...bindings import bind
from ...injector import create_injector
from ...keys import array
from ...providers import ConstProvider
from ...providers import SingletonProvider
from ...types import Binding
from ...types import Bindings
from ...types import Injector
from ...types import Key
from ...types import Provider
from ...types import ProviderFn


_ANONYMOUS_PRIVATE_SCOPE_COUNT = itertools.count()

PrivateScopeName = ta.NewType('PrivateScopeName', str)


@dc.dataclass(frozen=True, eq=False)
class PrivateScopeProvider(Provider):
    psn: PrivateScopeName
    bs: Bindings

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return Injector

    def required_keys(self) -> frozenset[Key | None]:
        raise NotImplementedError

    def children(self) -> ta.Iterable[Provider]:
        for b in self.bs.bindings():
            yield b.provider

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return create_injector(self.bs, i)
        return pfn


class _Exposed(ta.NamedTuple):
    key: Key


_EXPOSED_ARRAY_KEY = array(_Exposed)


def expose(arg: ta.Any) -> Binding:
    return as_(_EXPOSED_ARRAY_KEY, _Exposed(as_key(arg)))


@dc.dataclass(frozen=True, eq=False)
class ExposedPrivateProvider(Provider):
    psn: PrivateScopeName
    k: Key

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.k.cls

    def required_keys(self) -> frozenset[Key | None]:
        raise NotImplementedError

    def children(self) -> ta.Iterable[Provider]:
        return ()

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            pi = i.provide(Key(Injector, tag=self.psn))
            return pi.provide(self.k)
        return pfn


def private(*args: ta.Any, name: str | None = None) -> Bindings:
    if name is None:
        name = f'anon-{next(_ANONYMOUS_PRIVATE_SCOPE_COUNT)}'
    psn = PrivateScopeName(name)
    pbs = bind(*args, Binding(Key(PrivateScopeName), ConstProvider(PrivateScopeName, psn)))
    ebs: list[Binding] = [Binding(Key(Injector, tag=psn), SingletonProvider(PrivateScopeProvider(psn, pbs)))]  # noqa
    for b in pbs.bindings():
        if b.key == _EXPOSED_ARRAY_KEY:
            ek = check.isinstance(check.isinstance(b.provider, ConstProvider).v, _Exposed).key
            ebs.append(Binding(ek, ExposedPrivateProvider(psn, ek)))
    return bind(*ebs)


# @pytest.mark.skip('fixme')
def test_private():
    bs = bind(
        private(
            420,
            12.3,
            expose(int),
        ),
        private(
            lang.typed_lambda(str, f=float)(lambda f: f'{f}!'),
            12.3,
            expose(str),
        ),
    )
    i = create_injector(bs)
    assert i.provide(int) == 420
    assert i.provide(str) == '12.3!'
