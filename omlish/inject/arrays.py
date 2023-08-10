import typing as ta

from .. import dataclasses as dc
from .providers import Provider
from .providers import as_provider
from .types import Injector
from .types import Key
from .types import ProviderFn


T = ta.TypeVar('T')


@dc.dataclass(frozen=True)
class ArrayProvider(Provider):
    ty: type
    ps: ta.Sequence[Provider]

    sty: type

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.sty

    def provider_fn(self) -> ProviderFn:
        ps = [p.provider_fn() for p in self.ps]

        def pfn(i: Injector) -> ta.Any:
            rv = []
            for ep in ps:
                o = ep(i)
                rv.append(o)
            return rv

        return pfn


def array_provider(cls: type, *ps: Provider) -> ArrayProvider:
    return ArrayProvider(
        cls,
        ps,
        ta.Sequence[cls],
    )
