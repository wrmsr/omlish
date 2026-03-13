import typing as ta

from ..... import minichain as mc
from ....backends.types import ChatChoicesServiceBackendProvider
from ....backends.types import ChatChoicesStreamServiceBackendProvider


##


class ChatChoicesServiceProviderProxy:
    def __init__(
            self,
            service_provider: ChatChoicesServiceBackendProvider,
    ) -> None:
        super().__init__()

        self._service_provider = service_provider

    async def invoke(self, request: mc.ChatChoicesRequest) -> mc.ChatChoicesResponse:
        async with self._service_provider.provide_backend() as service:
            return await service.invoke(request)


class ChatChoicesStreamServiceProviderProxy:
    def __init__(
            self,
            service_provider: ChatChoicesStreamServiceBackendProvider,
    ) -> None:
        super().__init__()

        self._service_provider = service_provider

    async def invoke(self, request: mc.ChatChoicesStreamRequest) -> mc.ChatChoicesStreamResponse:
        async with mc.UseResources.or_new(request.options) as rs:
            service = await rs.enter_async_context(self._service_provider.provide_backend())
            return await service.invoke(request)
