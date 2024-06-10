import itertools
import typing as ta

from ... import cached
from ... import check
from ... import dataclasses as dc
from ... import lang
from ..bindings import as_
from ..bindings import as_key
from ..bindings import bind
from ..keys import multi
from ..providers import ConstProvider
from ..providers import SingletonProvider
from ..types import Binding
from ..types import Bindings
from ..types import Cls
from ..types import Injector
from ..types import Key
from ..types import Provider
from ..types import ProviderFn


_ANONYMOUS_PRIVATE_SCOPE_COUNT = itertools.count()

PrivateScopeName = ta.NewType('PrivateScopeName', str)


@dc.dataclass(frozen=True, eq=False)
class PrivateScopeProvider(Provider):
    psn: PrivateScopeName
    bs: Bindings

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return Injector

    @lang.cached_nullary
    def required_keys(self) -> frozenset[Key | None]:
        return frozenset(k for b in self.bs.bindings() for k in b.provider.required_keys())

    def children(self) -> ta.Iterable[Provider]:
        for b in self.bs.bindings():
            yield b.provider

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.create_child(self.bs)
        return pfn


@dc.dataclass(frozen=True)
class _Exposed:
    key: Key


_EXPOSED_MULTI_KEY = multi(_Exposed)


def expose(arg: ta.Any) -> Binding:
    return as_(_EXPOSED_MULTI_KEY, _Exposed(as_key(arg)))


@dc.dataclass(frozen=True, eq=False)
class ExposedPrivateProvider(Provider):
    psn: PrivateScopeName
    k: Key

    @cached.property
    def pik(self) -> Key:
        return Key(Injector, tag=self.psn)

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.k.cls

    def required_keys(self) -> frozenset[Key | None]:
        return frozenset([self.pik])

    def children(self) -> ta.Iterable[Provider]:
        return ()

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            pi = i.provide(self.pik)
            return pi.provide(self.k)
        return pfn


def private(*args: ta.Any, name: str | None = None) -> Bindings:
    if name is None:
        name = f'anon-{next(_ANONYMOUS_PRIVATE_SCOPE_COUNT)}'
    psn = PrivateScopeName(name)
    pbs = bind(*args, Binding(Key(PrivateScopeName), ConstProvider(PrivateScopeName, psn)))
    ebs: list[Binding] = [Binding(Key(Injector, tag=psn), SingletonProvider(PrivateScopeProvider(psn, pbs)))]  # noqa
    for b in pbs.bindings():
        if b.key == _EXPOSED_MULTI_KEY:
            ek = check.isinstance(check.isinstance(b.provider, ConstProvider).v, _Exposed).key
            ebs.append(Binding(ek, ExposedPrivateProvider(psn, ek)))
    return bind(*ebs)
