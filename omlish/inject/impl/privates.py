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
from ..bindings import Binding
from ..eagers import Eager
from ..elements import Element
from ..injector import Injector
from ..keys import Key
from ..privates import Expose
from ..privates import Private
from ..providers import Provider
from ..scopes import Singleton
from .elements import ElementCollection
from .injector import InjectorImpl
from .providers import InternalProvider
from .providers import ProviderImpl


##


_PRIVATE_COUNT = itertools.count()


@dc.dataclass(frozen=True)
class PrivateInjectorId(lang.Final):
    id: int


##


@dc.dataclass(eq=False)
class PrivateInjectorProviderImpl(ProviderImpl, lang.Final):
    id: PrivateInjectorId
    ec: ElementCollection

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return ()

    def provide(self, injector: Injector) -> ta.Any:
        return check.isinstance(injector, InjectorImpl).create_child(self.ec)


##


@dc.dataclass(eq=False)
class ExposedPrivateProviderImpl(ProviderImpl, lang.Final):
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
    def exposed_provider_impls(self) -> ta.Sequence[ExposedPrivateProviderImpl]:
        exs = self.element_collection().elements_of_type(Expose)
        return [ExposedPrivateProviderImpl(self.pik, ex.key) for ex in exs]

    @cached.function
    def owner_elements(self) -> ta.Iterable[Element]:
        lst: list[Element] = [
            Binding(self.pik, InternalProvider(self.private_provider_impl()), Singleton()),
            Eager(self.pik),
            *(Binding(ep.k, InternalProvider(ep)) for ep in self.exposed_provider_impls()),
        ]
        return lst
