"""
TODO:
 - add origin to Id
"""
import itertools
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ..injector import Injector
from ..keys import Key
from ..providers import Provider
from .elements import ElementCollection
from .injector import InjectorImpl
from .providers import ProviderImpl


_PRIVATE_COUNT = itertools.count()


@dc.dataclass(frozen=True)
class PrivateInjectorId(lang.Final):
    id: int


@dc.dataclass(frozen=True, eq=False)
class PrivateInjectorProviderImpl(ProviderImpl):
    id: PrivateInjectorId
    ec: ElementCollection

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return ()

    def provide(self, injector: Injector) -> ta.Any:
        return InjectorImpl(self.ec, check.isinstance(injector, InjectorImpl))


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
