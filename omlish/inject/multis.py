import typing as ta

from .. import dataclasses as dc
from .. import lang
from .providers import Provider
from .types import Cls
from .types import Injector
from .types import Key
from .types import ProviderFn


T = ta.TypeVar('T')

_ILLEGAL_MULTI_TYPES = (str, bytes, bytearray)


@dc.dataclass(frozen=True, eq=False)
class MultiProvider(Provider):
    ty: Cls
    ps: ta.Sequence[Provider]

    scls: Cls

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.scls

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
                if isinstance(o, _ILLEGAL_MULTI_TYPES):
                    raise TypeError(o)
                rv.extend(o)
            return rv

        return pfn


def multi_provider(cls: Cls, *ps: Provider) -> MultiProvider:
    return MultiProvider(
        cls,
        ps,
        # FIXME:
        ta.Sequence[cls],  # type: ignore
    )
