from ..... import minichain as mc
from ....backends.types import BackendProvider


##


class ChatChoicesServiceBackendProviderProxy:
    def __init__(
            self,
            service_provider: BackendProvider[mc.ChatChoicesService],
    ) -> None:
        super().__init__()

        self._service_provider = service_provider

    async def invoke(self, request: mc.ChatChoicesRequest) -> mc.ChatChoicesResponse:
        async with self._service_provider.provide_backend() as service:
            return await service.invoke(request)


class ChatChoicesStreamServiceBackendProviderProxy:
    def __init__(
            self,
            service_provider: BackendProvider[mc.ChatChoicesStreamService],
    ) -> None:
        super().__init__()

        self._service_provider = service_provider

    async def invoke(self, request: mc.ChatChoicesStreamRequest) -> mc.ChatChoicesStreamResponse:
        async with mc.UseResources.or_new(request.options) as rs:
            service = await rs.enter_async_context(self._service_provider.provide_backend())
            return await service.invoke(request)
