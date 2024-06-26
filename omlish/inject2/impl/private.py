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


@dc.dataclass(eq=False)
class PrivateInjectorProviderImpl(ProviderImpl):
    id: PrivateInjectorId
    ec: ElementCollection
    ip: Provider | None = None

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (check.not_none(self.ip),)

    def provide(self, injector: Injector) -> ta.Any:
        return InjectorImpl(self.ec, check.isinstance(injector, InjectorImpl))


##


@dc.dataclass(eq=False)
class ExposedPrivateProviderImpl(ProviderImpl):
    pik: Key
    k: Key
    ip: Provider | None = None

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (check.not_none(self.ip),)

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
        raise TypeError


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
    def exposed_provider_impls(self) -> ta.Mapping[Key, ta.Sequence[ExposedPrivateProviderImpl]]:
        exs = self.element_collection().elements_of_type(Expose)
        dct: dict[Key, list[ExposedPrivateProviderImpl]] = {}
        for ex in exs:
            dct.setdefault(ex.key, []).append(ExposedPrivateProviderImpl(self.pik, ex.key))
        return dct

    @cached.function
    def internal_providers(self) -> ta.Mapping[Key, list[InternalProvider]]:
        def bind_ip(impl, cls):
            check.none(impl.ip)
            impl.ip = ip = InternalProvider(impl, cls)
            return ip

        dct: dict[Key, list[InternalProvider]] = {
            self.pik: [bind_ip(self.private_provider_impl(), InjectorImpl)],
        }
        for k, epis in self.exposed_provider_impls().items():
            dct.setdefault(k, []).extend(bind_ip(epi, k.cls) for epi in epis)
        return dct
