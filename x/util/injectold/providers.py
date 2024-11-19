import dataclasses as dc
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_isinstance

from .keys import as_key
from .types import Binding
from .types import Bindings
from .types import Injector
from .types import Key
from .types import Provider
from .types import ProviderFn


##


def as_provider(o: ta.Any) -> Provider:
    check_not_isinstance(o, (Binding, Bindings))
    if isinstance(o, Provider):
        return o
    if isinstance(o, Key):
        return LinkProvider(o)
    if isinstance(o, type):
        return ctor(o)
    if callable(o):
        return fn(o)
    return ConstProvider(o)


##


@dc.dataclass(frozen=True)
class FnProvider(Provider):
    fn: ta.Any

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.fn)

        return pfn


def fn(fn: ta.Any) -> Provider:
    check_not_isinstance(fn, type)
    return FnProvider(fn)


##


@dc.dataclass(frozen=True)
class CtorProvider(Provider):
    cls: type

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.cls)

        return pfn


def ctor(cls: type) -> Provider:
    return CtorProvider(check_isinstance(cls, type))


##


@dc.dataclass(frozen=True)
class ConstProvider(Provider):
    v: ta.Any

    def provider_fn(self) -> ProviderFn:
        return lambda _: self.v


def const(v: ta.Any) -> Provider:
    return ConstProvider(v)


##


@dc.dataclass(frozen=True)
class SingletonProvider(Provider):
    p: Provider

    def provider_fn(self) -> ProviderFn:
        v = not_set = object()

        def pfn(i: Injector) -> ta.Any:
            nonlocal v
            if v is not_set:
                v = ufn(i)
            return v

        ufn = self.p.provider_fn()
        return pfn


def singleton(p: ta.Any) -> Provider:
    return SingletonProvider(as_provider(p))


##


@dc.dataclass(frozen=True)
class LinkProvider(Provider):
    k: Key

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.provide(self.k)

        return pfn


def link(k: ta.Any) -> Provider:
    return LinkProvider(as_key(k))
