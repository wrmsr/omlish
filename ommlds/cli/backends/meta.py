import contextlib
import typing as ta

from ... import minichain as mc
from .types import BackendProvider


ServiceT = ta.TypeVar('ServiceT', bound=mc.Service)
StreamServiceT = ta.TypeVar('StreamServiceT', bound=mc.Service)


##


class FirstInWinsBackendProvider(BackendProvider[ServiceT]):
    def __init__(
            self,
            backend_providers: ta.AbstractSet[BackendProvider],
    ) -> None:
        super().__init__()

        self._backend_providers = [ta.cast(BackendProvider[ServiceT], bp) for bp in backend_providers]

    def provide_backend(self) -> ta.AsyncContextManager[ServiceT]:
        @contextlib.asynccontextmanager
        async def inner():
            from ...minichain.wrappers.firstinwins import AsyncioFirstInWinsService

            async with contextlib.AsyncExitStack() as aes:
                svcs = [
                    await aes.enter_async_context(bp.provide_backend())
                    for bp in self._backend_providers
                ]
                yield AsyncioFirstInWinsService(*svcs)

        return inner()


##


class RetryBackendProvider(BackendProvider):
    def __init__(
            self,
            backend_provider: BackendProvider,
    ) -> None:
        super().__init__()

        self._backend_provider = backend_provider

    def provide_backend(self) -> ta.AsyncContextManager:
        @contextlib.asynccontextmanager
        async def inner():
            async with contextlib.AsyncExitStack() as aes:
                yield mc.RetryService(
                    await aes.enter_async_context(self._backend_provider.provide_backend()),
                )

        return inner()


##


class RetryStreamBackendProvider(BackendProvider):
    def __init__(
            self,
            backend_provider: BackendProvider,
    ) -> None:
        super().__init__()

        self._backend_provider = backend_provider

    def provide_backend(self) -> ta.AsyncContextManager:
        @contextlib.asynccontextmanager
        async def inner():
            async with contextlib.AsyncExitStack() as aes:
                yield mc.RetryStreamService(
                    await aes.enter_async_context(self._backend_provider.provide_backend()),
                )

        return inner()
