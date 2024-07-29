"""
TODO:
 - required_keys
"""
import abc
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ..injector import Injector
from ..inspect import KwargsTarget
from ..providers import ConstProvider
from ..providers import CtorProvider
from ..providers import FnProvider
from ..providers import LinkProvider
from ..providers import Provider
from .inspect import build_kwargs_target


##


class ProviderImpl(lang.Abstract):
    @property
    @abc.abstractmethod
    def providers(self) -> ta.Iterable[Provider]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, injector: Injector) -> ta.Any:
        raise NotImplementedError


##


@dc.dataclass(frozen=True, eq=False)
class InternalProvider(Provider):
    impl: ProviderImpl

    def provided_ty(self) -> rfl.Type | None:
        raise TypeError


##


@dc.dataclass(frozen=True, eq=False)
class CallableProviderImpl(ProviderImpl, lang.Final):
    p: FnProvider | CtorProvider
    kt: KwargsTarget

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provide(self, injector: Injector) -> ta.Any:
        return injector.inject(self.kt)


##


@dc.dataclass(frozen=True, eq=False)
class ConstProviderImpl(ProviderImpl, lang.Final):
    p: ConstProvider

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provide(self, injector: Injector) -> ta.Any:
        return self.p.v


##


@dc.dataclass(frozen=True, eq=False)
class LinkProviderImpl(ProviderImpl, lang.Final):
    p: LinkProvider

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provide(self, injector: Injector) -> ta.Any:
        return injector.provide(self.p.k)


##


PROVIDER_IMPLS_BY_PROVIDER: dict[type[Provider], ta.Callable[..., ProviderImpl]] = {
    FnProvider: lambda p: CallableProviderImpl(p, build_kwargs_target(p.fn)),
    CtorProvider: lambda p: CallableProviderImpl(p, build_kwargs_target(p.ty)),
    ConstProvider: ConstProviderImpl,
    LinkProvider: LinkProviderImpl,
    InternalProvider: lambda p: p.impl,
}


def make_provider_impl(p: Provider) -> ProviderImpl:
    try:
        fac = PROVIDER_IMPLS_BY_PROVIDER[type(p)]
    except KeyError:
        pass
    else:
        return fac(p)

    raise TypeError(p)
