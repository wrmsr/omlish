import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ..elements import Element
from ..injector import AsyncInjector
from ..multis import MapBinding
from ..multis import MapProvider
from ..multis import SetBinding
from ..multis import SetProvider
from ..providers import LinkProvider
from ..providers import Provider
from .providers import LinkProviderImpl
from .providers import ProviderImpl


##


@dc.dataclass(frozen=True, eq=False)
class SetProviderImpl(ProviderImpl, lang.Final):
    ps: ta.Sequence[ProviderImpl]

    @property
    def providers(self) -> ta.Iterator[Provider]:
        for p in self.ps:
            yield from p.providers

    async def provide(self, injector: AsyncInjector) -> ta.Any:
        rv = set()
        for ep in self.ps:
            o = await ep.provide(injector)
            rv.add(o)
        return rv


@dc.dataclass(frozen=True, eq=False)
class MapProviderImpl(ProviderImpl, lang.Final):
    class Entry(ta.NamedTuple):
        k: ta.Any
        v: ProviderImpl

    es: ta.Sequence[Entry]

    @property
    def providers(self) -> ta.Iterator[Provider]:
        for e in self.es:
            yield from e.v.providers

    async def provide(self, injector: AsyncInjector) -> ta.Any:
        rv = {}
        for e in self.es:
            o = await e.v.provide(injector)
            rv[e.k] = o
        return rv


def make_multi_provider_impl(p: Provider, es_by_ty: ta.MutableMapping[type, list[Element]]) -> ProviderImpl:
    if isinstance(p, SetProvider):
        sbs: ta.Iterable[SetBinding] = es_by_ty.pop(SetBinding, ())  # type: ignore
        check.empty(es_by_ty)
        return SetProviderImpl([
            LinkProviderImpl(LinkProvider(sb.dst))
            for sb in sbs
        ])

    elif isinstance(p, MapProvider):
        mbs: ta.Iterable[MapBinding] = es_by_ty.pop(MapBinding, ())  # type: ignore
        check.empty(es_by_ty)
        return MapProviderImpl([
            MapProviderImpl.Entry(
                mb.map_key,
                LinkProviderImpl(LinkProvider(mb.dst)),
            )
            for mb in mbs
        ])

    else:
        raise TypeError(p)
