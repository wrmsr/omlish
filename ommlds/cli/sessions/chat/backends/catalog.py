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


class CatalogBackendProvider(BackendProvider[ServiceT], lang.Abstract):
    class Instantiator(lang.Func2['mc.BackendCatalog.Backend', BackendConfigs | None, ta.Awaitable[ta.Any]]):
        pass

    def __init__(
            self,
            *,
            name: BackendName,
            catalog: 'mc.BackendCatalog',
            configs: BackendConfigs | None = None,
            instantiator: Instantiator | None = None,
    ) -> None:
        super().__init__()

        self._name = name
        self._catalog = catalog
        self._configs = configs
        if instantiator is None:
            instantiator = CatalogBackendProvider.Instantiator(lang.as_async(lambda be, cfgs: be.factory(*cfgs or [])))
        self._instantiator = instantiator

    @contextlib.asynccontextmanager
    async def _provide_backend(self, cls: type[ServiceT]) -> ta.AsyncIterator[ServiceT]:
        be = self._catalog.get_backend(cls, self._name)

        service: ServiceT
        async with lang.async_or_sync_maybe_managing(await self._instantiator(be, self._configs)) as service:
            yield service


class CatalogChatChoicesServiceBackendProvider(
    CatalogBackendProvider['mc.ChatChoicesService'],
    ChatChoicesServiceBackendProvider,
):
    def provide_backend(self) -> ta.AsyncContextManager['mc.ChatChoicesService']:
        return self._provide_backend(mc.ChatChoicesService)  # type: ignore[type-abstract]


class CatalogChatChoicesStreamServiceBackendProvider(
    CatalogBackendProvider['mc.ChatChoicesStreamService'],
    ChatChoicesStreamServiceBackendProvider,
):
    def provide_backend(self) -> ta.AsyncContextManager['mc.ChatChoicesStreamService']:
        return self._provide_backend(mc.ChatChoicesStreamService)  # type: ignore[type-abstract]
