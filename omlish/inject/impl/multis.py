import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..injector import Injector
from ..providers import Provider
from .providers import ProviderImpl


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
            rv.add(o)
        return rv


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
        rv = {}
        for e in self.es:
            o = e.v.provide(injector)
            rv[e.k] = o
        return rv
