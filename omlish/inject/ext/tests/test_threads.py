import threading
import typing as ta

from ...providers import CtorProvider
from ...providers import SingletonProvider
from ...types import Binding
from ...types import Injector
from ...types import Key
from ...types import Provider
from ...types import ProviderFn


class _ThreadLocals:
    def __init__(self) -> None:
        super().__init__()
        self.tls = threading.local()


_THREAD_LOCALS_KEY = Key(_ThreadLocals)


class ThreadLocalProvider(Provider):
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.p.provided_cls()

    def required_keys(self) -> frozenset[Key | None]:
        return frozenset([*self.p.required_keys(), _THREAD_LOCALS_KEY])

    def children(self) -> ta.Iterable[Provider]:
        return (self.p,)

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            tls = i.provide(_THREAD_LOCALS_KEY).tls
            raise NotImplementedError
        return pfn


def thread_local(p: ta.Any) -> Provider:
    return ThreadLocalProvider(p)


def bind_thread_locals() -> Binding:
    return Binding(_THREAD_LOCALS_KEY, SingletonProvider(CtorProvider(_ThreadLocals)))


def test_threads():
    pass
