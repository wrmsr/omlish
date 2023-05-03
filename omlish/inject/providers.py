import typing as ta

from .. import check
from .. import dataclasses as dc
from .inspect import signature
from .keys import as_key
from .types import Binding
from .types import Bindings
from .types import Key
from .types import Provider
from .types import ProviderFn
from .types import _BindingGen
from .types import _ProviderGen


##


def as_provider(o: ta.Any) -> Provider:
    check.not_isinstance(o, (Binding, _BindingGen, Bindings))
    if isinstance(o, Provider):
        return o
    if isinstance(o, _ProviderGen):
        return o._gen_provider()  # noqa
    if isinstance(o, Key):
        return LinkProvider(o)
    if callable(o):
        return fn(o)
    return ConstProvider(type(o), o)


##


@dc.dataclass(frozen=True)
class FnProvider(Provider):
    cls: type
    fn: ta.Any

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.cls

    def provider_fn(self) -> ProviderFn:
        def fn(i):
            return i.inject(self.fn)

        return fn


def fn(fn: ta.Any, cls: ta.Optional[type] = None) -> Provider:
    sig = signature(fn)
    if cls is None:
        cls = check.isinstance(sig.return_annotation, type)
    return FnProvider(cls, fn)


##


@dc.dataclass(frozen=True)
class ConstProvider(Provider):
    cls: type
    v: ta.Any

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.cls

    def provider_fn(self) -> ProviderFn:
        return lambda _: self.v


def const(v: ta.Any, cls: ta.Optional[type] = None) -> Provider:
    if cls is None:
        cls = type(v)
    return ConstProvider(cls, v)


##


@dc.dataclass(frozen=True)
class SingletonProvider(Provider):
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.p.provided_cls(rec)

    def provider_fn(self) -> ProviderFn:
        def fn(i):
            nonlocal v
            if v is not_set:
                v = pfn(i)
            return v

        pfn = self.p.provider_fn()
        v = not_set = object()
        return fn


def singleton(p: Provider) -> Provider:
    return SingletonProvider(p)


##


@dc.dataclass(frozen=True)
class LinkProvider(Provider):
    k: Key

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return rec(self.k)

    def provider_fn(self) -> ProviderFn:
        def fn(i):
            return i.provide(self.k)

        return fn


def link(k: ta.Any) -> Provider:
    return LinkProvider(as_key(k))
