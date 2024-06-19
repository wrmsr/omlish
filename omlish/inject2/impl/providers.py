import abc
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..injector import Injector
from ..inspect import KwargsTarget
from ..providers import ConstProvider
from ..providers import CtorProvider
from ..providers import FnProvider
from ..providers import LinkProvider
from ..providers import Provider
from .inspect import build_kwargs_target


class ProviderImpl(lang.Abstract):
    @property
    @abc.abstractmethod
    def providers(self) -> ta.Iterable[Provider]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, i: Injector) -> ta.Any:
        raise NotImplementedError


@dc.dataclass(frozen=True, eq=False)
class CallableProviderImpl(ProviderImpl, lang.Final):
    p: FnProvider | CtorProvider
    kt: KwargsTarget

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provide(self, i: Injector) -> ta.Any:
        return i.inject(self.kt)


@dc.dataclass(frozen=True, eq=False)
class ConstProviderImpl(ProviderImpl, lang.Final):
    p: ConstProvider

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provide(self, i: Injector) -> ta.Any:
        return self.p.v


@dc.dataclass(frozen=True, eq=False)
class LinkProviderImpl(ProviderImpl, lang.Final):
    p: LinkProvider

    @property
    def providers(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provide(self, i: Injector) -> ta.Any:
        return i.provide(self.p.k)


_ILLEGAL_MULTI_TYPES = (str, bytes, bytearray)


@dc.dataclass(frozen=True, eq=False)
class MultiProviderImpl(ProviderImpl, lang.Final):
    ps: ta.Sequence[ProviderImpl]

    @property
    def providers(self) -> ta.Iterable[Provider]:
        for p in self.ps:
            yield from p.providers

    def provide(self, i: Injector) -> ta.Any:
        rv = []
        for ep in self.ps:
            o = ep.provide(i)
            if isinstance(o, _ILLEGAL_MULTI_TYPES):
                raise TypeError(o)
            rv.extend(o)
        return rv


def make_provider_impl(p: Provider) -> ProviderImpl:
    if isinstance(p, FnProvider):
        return CallableProviderImpl(p, build_kwargs_target(p.fn))
    if isinstance(p, CtorProvider):
        return CallableProviderImpl(p, build_kwargs_target(p.cls))
    if isinstance(p, ConstProvider):
        return ConstProviderImpl(p)
    if isinstance(p, LinkProvider):
        return LinkProviderImpl(p)
    raise TypeError(p)
