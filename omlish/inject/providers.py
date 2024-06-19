import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .inspect import KwargsTarget
from .inspect import build_kwargs_target
from .inspect import signature
from .keys import as_key
from .types import Binding
from .types import Bindings
from .types import Cls
from .types import Injector
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
    if isinstance(o, type):
        return ctor(o)
    if callable(o):
        return fn(o)
    return ConstProvider(type(o), o)


##


@dc.dataclass(frozen=True, eq=False)
class FnProvider(Provider):
    cls: Cls
    fn: ta.Any
    kt: KwargsTarget

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.cls

    @lang.cached_function
    def required_keys(self) -> frozenset[Key | None]:
        return frozenset(kw.key for kw in self.kt.kwargs)

    def children(self) -> ta.Iterable[Provider]:
        return ()

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.fn)
        return pfn


def fn(fn: ta.Any, cls: ta.Optional[type] = None) -> Provider:
    check.not_isinstance(fn, type)
    sig = signature(fn)
    if cls is None:
        cls = check.isinstance(sig.return_annotation, type)
    kt = build_kwargs_target(fn)
    return FnProvider(cls, fn, kt)


##


@dc.dataclass(frozen=True, eq=False)
class CtorProvider(Provider):
    cls: type
    kt: KwargsTarget

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.cls

    @lang.cached_function
    def required_keys(self) -> frozenset[Key | None]:
        return frozenset(kw.key for kw in self.kt.kwargs)

    def children(self) -> ta.Iterable[Provider]:
        return ()

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.cls)
        return pfn


def ctor(cls: type) -> Provider:
    check.isinstance(cls, type)
    kt = build_kwargs_target(cls)
    return CtorProvider(cls, kt)


##


@dc.dataclass(frozen=True, eq=False)
class ConstProvider(Provider):
    cls: Cls
    v: ta.Any

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.cls

    def required_keys(self) -> frozenset[Key | None]:
        return frozenset()

    def children(self) -> ta.Iterable[Provider]:
        return ()

    def provider_fn(self) -> ProviderFn:
        return lambda _: self.v


def const(v: ta.Any, cls: ta.Optional[Cls] = None) -> Provider:
    if cls is None:
        cls = type(v)
    return ConstProvider(cls, v)


##


@dc.dataclass(frozen=True, eq=False)
class SingletonProvider(Provider):
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.p.provided_cls(rec)

    def required_keys(self) -> frozenset[Key | None]:
        return self.p.required_keys()

    def children(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provider_fn(self) -> ProviderFn:
        v = not_set = object()
        ufn = self.p.provider_fn()

        def pfn(i: Injector) -> ta.Any:
            nonlocal v
            if v is not_set:
                v = ufn(i)
            return v

        return pfn


def singleton(p: ta.Any) -> Provider:
    return SingletonProvider(as_provider(p))


##


@dc.dataclass(frozen=True, eq=False)
class LinkProvider(Provider):
    k: Key

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return rec(self.k)

    def required_keys(self) -> frozenset[Key | None]:
        return frozenset([self.k])

    def children(self) -> ta.Iterable[Provider]:
        return ()

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.provide(self.k)

        return pfn


def link(k: ta.Any) -> Provider:
    return LinkProvider(as_key(k))
