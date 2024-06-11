import threading
import typing as ta

from ... import dataclasses as dc
from ..providers import SingletonProvider
from ..providers import as_provider
from ..providers import ctor
from ..types import Binding
from ..types import Cls
from ..types import Injector
from ..types import Key
from ..types import Provider
from ..types import ProviderFn


class _ThreadLocals:
    def __init__(self) -> None:
        super().__init__()
        self.tls = threading.local()


_THREAD_LOCALS_KEY = Key(_ThreadLocals)


@dc.dataclass(frozen=True, eq=False)
class ThreadLocalProvider(Provider):
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        return self.p.provided_cls(rec)

    def required_keys(self) -> frozenset[Key | None]:
        return frozenset([*self.p.required_keys(), _THREAD_LOCALS_KEY])

    def children(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provider_fn(self) -> ProviderFn:
        ipfn = self.p.provider_fn()

        def pfn(i: Injector) -> ta.Any:
            tls = i.provide(_THREAD_LOCALS_KEY).tls
            try:
                values = tls.values
            except AttributeError:
                values = tls.values = {}
            try:
                return values[self]
            except KeyError:
                values[self] = v = ipfn(i)
                return v

        return pfn


def thread_local(p: ta.Any) -> Provider:
    return ThreadLocalProvider(as_provider(p))


def bind_thread_locals() -> Binding:
    return Binding(_THREAD_LOCALS_KEY, SingletonProvider(ctor(_ThreadLocals)))
