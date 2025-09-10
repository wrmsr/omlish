"""
TODO:
 - required_keys
"""
import abc
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..injector import AsyncInjector
from ..inspect import KwargsTarget
from ..providers import AsyncFnProvider
from ..providers import ConstProvider
from ..providers import CtorProvider
from ..providers import FnProvider
from ..providers import LinkProvider
from ..providers import Provider


##


class ProviderImpl(lang.Abstract):
    @property
    @abc.abstractmethod
    def providers(self) -> ta.Iterable[Provider]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, injector: AsyncInjector) -> ta.Awaitable[ta.Any]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True, eq=False)
class InternalProvider(Provider):
    impl: ProviderImpl


##


@dc.dataclass(frozen=True, eq=False)
class AsyncCallableProviderImpl(ProviderImpl, lang.Final):
    p: AsyncFnProvider
    kt: KwargsTarget

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    async def provide(self, injector: AsyncInjector) -> ta.Any:
        return await (await injector.inject(self.kt))


##


@dc.dataclass(frozen=True, eq=False)
class CallableProviderImpl(ProviderImpl, lang.Final):
    p: FnProvider | CtorProvider
    kt: KwargsTarget

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    async def provide(self, injector: AsyncInjector) -> ta.Any:
        return await injector.inject(self.kt)


##


@dc.dataclass(frozen=True, eq=False)
class ConstProviderImpl(ProviderImpl, lang.Final):
    p: ConstProvider

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    async def provide(self, injector: AsyncInjector) -> ta.Any:
        return self.p.v


##


@dc.dataclass(frozen=True, eq=False)
class LinkProviderImpl(ProviderImpl, lang.Final):
    p: LinkProvider

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    async def provide(self, injector: AsyncInjector) -> ta.Any:
        return await injector.provide(self.p.k)
