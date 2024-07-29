import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..injector import Injector
from ..multis import MapProvider
from ..multis import SetProvider
from ..providers import Provider
from .providers import PROVIDER_IMPLS_BY_PROVIDER
from .providers import ProviderImpl


_ILLEGAL_MULTI_TYPES = (str, bytes, bytearray)


@dc.dataclass(frozen=True, eq=False)
class SetProviderImpl(ProviderImpl, lang.Final):
    ps: ta.Sequence[ProviderImpl]

    @property
    def providers(self) -> ta.Iterable[Provider]:
        for p in self.ps:
            yield from p.providers

    def provide(self, injector: Injector) -> ta.Any:
        rv = set()
        for ep in self.ps:
            o = ep.provide(injector)
            if isinstance(o, _ILLEGAL_MULTI_TYPES):
                raise TypeError(o)
            rv.add(o)
        return rv


PROVIDER_IMPLS_BY_PROVIDER[SetProvider] = SetProviderImpl


@dc.dataclass(frozen=True, eq=False)
class MapProviderImpl(ProviderImpl, lang.Final):
    class Entry(ta.NamedTuple):
        k: ta.Any
        v: ProviderImpl

    es: ta.Sequence[Entry]

    @property
    def providers(self) -> ta.Iterable[Provider]:
        for e in self.es:
            yield from e.v.providers

    def provide(self, injector: Injector) -> ta.Any:
        rv = set()
        for ep in self.ps:
            o = ep.provide(injector)
            if isinstance(o, _ILLEGAL_MULTI_TYPES):
                raise TypeError(o)
            rv.add(o)
        return rv


PROVIDER_IMPLS_BY_PROVIDER[MapProvider] = MapProviderImpl
