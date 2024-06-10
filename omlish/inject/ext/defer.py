import contextlib
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..bindings import bind
from ..injector import create_injector
from ..providers import as_provider
from ..providers import singleton
from ..types import Bindings
from ..types import Cls
from ..types import Injector
from ..types import Key
from ..types import Provider
from ..types import ProviderFn


@dc.dataclass(frozen=True, eq=False)
class ClosingProvider(Provider):
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.p.provided_cls(rec)

    def required_keys(self) -> frozenset[Key | None]:
        return self.p.required_keys()

    def children(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            v = ufn(i)
            i[contextlib.ExitStack].enter_context(lang.defer(v.close))  # noqa
            return v

        ufn = self.p.provider_fn()
        return pfn


def closing(obj: ta.Any) -> Provider:
    return ClosingProvider(as_provider(obj))


@contextlib.contextmanager
def create_defer_injector(bs: Bindings, p: ta.Optional[Injector] = None) -> ta.Generator[Injector, None, None]:
    i = create_injector(bind(
        bs,
        singleton(contextlib.ExitStack),
    ), p)
    with i[contextlib.ExitStack]:
        yield i
