"""
TODO:
 - add origin to Id
"""
import itertools
import typing as ta

from ... import cached
from ... import check
from ... import dataclasses as dc
from ... import lang
from ..injector import Injector
from ..keys import Key
from ..private import Expose
from ..private import Private
from ..providers import Provider
from ..types import Cls
from .elements import ElementCollection
from .injector import InjectorImpl
from .providers import ProviderImpl


##


_PRIVATE_COUNT = itertools.count()


@dc.dataclass(frozen=True)
class PrivateInjectorId(lang.Final):
    id: int


##


@dc.dataclass(frozen=True, eq=False)
class PrivateInjectorProviderImpl(ProviderImpl):
    id: PrivateInjectorId
    ec: ElementCollection

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return ()

    def provide(self, injector: Injector) -> ta.Any:
        return InjectorImpl(self.ec, check.isinstance(injector, InjectorImpl))


##


@dc.dataclass(frozen=True, eq=False)
class ExposedPrivateProviderImpl(ProviderImpl):
    pik: Key
    k: Key

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return ()

    def provide(self, injector: Injector) -> ta.Any:
        pi = injector.provide(self.pik)
        return pi.provide(self.k)


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class InternalProvider(Provider):
    impl: ProviderImpl
    cls: Cls

    def provided_cls(self) -> Cls | None:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class PrivateInfo(lang.Final):
    owner: ElementCollection
    p: Private

    @cached.property
    def id(self) -> PrivateInjectorId:
        return PrivateInjectorId(next(_PRIVATE_COUNT))

    @cached.property
    def pik(self) -> Key:
        return Key(InjectorImpl, tag=self.id)

    @cached.function
    def element_collection(self) -> ElementCollection:
        return ElementCollection(self.p.elements)

    ##

    @cached.function
    def private_provider_impl(self) -> PrivateInjectorProviderImpl:
        return PrivateInjectorProviderImpl(self.id, self.element_collection())

    @cached.function
    def exposed_provider_impls(self) -> ta.Mapping[Key, ExposedPrivateProviderImpl]:
        exs = self.element_collection().elements_of_type(Expose)
        raise NotImplementedError

    @cached.function
    def internal_providers(self) -> ta.Mapping[Key, InternalProvider]:
        ppi = self.private_provider_impl()
        epis = self.exposed_provider_impls()
        raise NotImplementedError
