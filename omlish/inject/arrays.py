import typing as ta

from .. import dataclasses as dc
from .. import lang
from .providers import Provider
from .types import Injector
from .types import Key
from .types import ProviderFn


T = ta.TypeVar('T')


@dc.dataclass(frozen=True, eq=False)
class ArrayProvider(Provider):
    ty: type
    ps: ta.Sequence[Provider]

    sty: type

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.sty

    @lang.cached_nullary
    def required_keys(self) -> frozenset[Key | None]:
        return frozenset(k for c in self.ps for k in c.required_keys())

    def children(self) -> ta.Iterable[Provider]:
        yield from self.ps

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
        # FIXME:
        ta.Sequence[cls],  # type: ignore
    )
