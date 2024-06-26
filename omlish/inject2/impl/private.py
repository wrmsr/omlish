"""
TODO:
 - add origin to Id
"""
import itertools
import typing as ta

from .. import Cls
from ... import check
from ... import dataclasses as dc
from ... import lang
from ..injector import Injector
from ..keys import Key
from ..private import Expose
from ..private import Private
from ..providers import Provider
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
    id: PrivateInjectorId
    k: Key

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return ()

    def provide(self, injector: Injector) -> ta.Any:
        pi = injector.provide(Key(Injector, tag=self.id))
        return pi.provide(self.k)


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ExposedPrivateProvider(Provider):
    pid: PrivateInjectorId
    k: Key

    def provided_cls(self) -> Cls | None:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class PrivateInfo(lang.Final):
    owner: ElementCollection
    p: Private

    @lang.cached_function
    def id(self) -> PrivateInjectorId:
        return PrivateInjectorId(next(_PRIVATE_COUNT))

    @lang.cached_function
    def element_collection(self) -> ElementCollection:
        return ElementCollection(self.p.elements)

    @lang.cached_function
    def exposed_providers(self) -> ta.Mapping[Key, ExposedPrivateProviderImpl]:
        exs = self.element_collection().elements_of_type(Expose)
        raise NotImplementedError
