import contextlib
import typing as ta

from omlish import lang

from ..... import minichain as mc
from .types import BackendConfigs
from .types import BackendName
from .types import BackendProvider
from .types import ChatChoicesServiceBackendProvider
from .types import ChatChoicesStreamServiceBackendProvider
from .types import ServiceT


##


class _CatalogBackendProvider(BackendProvider[ServiceT], lang.Abstract):
    def __init__(
            self,
            *,
            name: BackendName,
            catalog: mc.BackendCatalog,
            configs: BackendConfigs | None = None,
    ) -> None:
        super().__init__()

        self._name = name
        self._catalog = catalog
        self._configs = configs

    @contextlib.asynccontextmanager
    async def _provide_backend(self, cls: type[ServiceT]) -> ta.AsyncIterator[ServiceT]:
        service: ServiceT
        async with lang.async_maybe_managing(self._catalog.get_backend(
                cls,
                self._name,
                *(self._configs or []),
        )) as service:
            yield service


class CatalogChatChoicesServiceBackendProvider(
    _CatalogBackendProvider[mc.ChatChoicesService],
    ChatChoicesServiceBackendProvider,
):
    def provide_backend(self) -> ta.AsyncContextManager[mc.ChatChoicesService]:
        return self._provide_backend(mc.ChatChoicesService)  # type: ignore[type-abstract]


class CatalogChatChoicesStreamServiceBackendProvider(
    _CatalogBackendProvider[mc.ChatChoicesStreamService],
    ChatChoicesStreamServiceBackendProvider,
):
    def provide_backend(self) -> ta.AsyncContextManager[mc.ChatChoicesStreamService]:
        return self._provide_backend(mc.ChatChoicesStreamService)  # type: ignore[type-abstract]
