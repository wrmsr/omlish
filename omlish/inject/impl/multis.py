import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ..injector import Injector
from ..providers import Provider
from .providers import ProviderImpl


_ILLEGAL_MULTI_TYPES = (str, bytes, bytearray)


def _unnest_multi_providers(ps: ta.Iterable[ProviderImpl]) -> ta.Sequence[ProviderImpl]:
    lst = []

    def rec(o):
        if isinstance(o, MultiProviderImpl):
            for c in o.ps:
                rec(c)
        else:
            lst.append(check.isinstance(o, ProviderImpl))

    for o in ps:
        rec(o)
    return tuple(lst)


@dc.dataclass(frozen=True, eq=False)
class MultiProviderImpl(ProviderImpl, lang.Final):
    ps: ta.Sequence[ProviderImpl] = dc.xfield(coerce=_unnest_multi_providers)

    @property
    def providers(self) -> ta.Iterable[Provider]:
        for p in self.ps:
            yield from p.providers

    def provide(self, injector: Injector) -> ta.Any:
        rv = []
        for ep in self.ps:
            o = ep.provide(injector)
            if isinstance(o, _ILLEGAL_MULTI_TYPES):
                raise TypeError(o)
            rv.extend(o)
        return rv
