import contextlib
import typing as ta

from ... import minichain as mc
from .types import BackendProvider


ServiceT = ta.TypeVar('ServiceT', bound=mc.Service)


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
            from ...minichain.meta.firstinwins import AsyncioFirstInWinsService

            async with contextlib.AsyncExitStack() as aes:
                svcs = [
                    await aes.enter_async_context(bp.provide_backend())
                    for bp in self._backend_providers
                ]
                yield AsyncioFirstInWinsService(*svcs)

        return inner()
