from ..... import minichain as mc


##


class ChatChoicesServiceBackendProviderProxy:
    def __init__(
            self,
            service_provider: mc.ServiceProvider[mc.ChatChoicesService],
    ) -> None:
        super().__init__()

        self._service_provider = service_provider

    async def invoke(self, request: mc.ChatChoicesRequest) -> mc.ChatChoicesResponse:
        async with self._service_provider.provide_service() as service:
            return await service.invoke(request)


class ChatChoicesStreamServiceBackendProviderProxy:
    def __init__(
            self,
            service_provider: mc.ServiceProvider[mc.ChatChoicesStreamService],
    ) -> None:
        super().__init__()

        self._service_provider = service_provider

    async def invoke(self, request: mc.ChatChoicesStreamRequest) -> mc.ChatChoicesStreamResponse:
        async with mc.UseResources.or_new(request.options) as rs:
            service = await rs.enter_async_context(self._service_provider.provide_service())
            return await service.invoke(request)
