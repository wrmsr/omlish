import typing as ta

from omlish import check
from omlish import lang

from ...... import minichain as mc
from .....backends.types import ChatChoicesServiceBackendProvider
from .....backends.types import ChatChoicesStreamServiceBackendProvider
from .types import AiChatGenerator
from .types import StreamAiChatGenerator


##


class ChatChoicesServiceOptionsProvider(lang.Func0[ta.Sequence['mc.ChatChoicesOptions']]):
    pass


ChatChoicesServiceOptionsProviders = ta.NewType('ChatChoicesServiceOptionsProviders', ta.Sequence[ChatChoicesServiceOptionsProvider])  # noqa


##


class ChatChoicesServiceAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            service_provider: ChatChoicesServiceBackendProvider,
            *,
            options: ChatChoicesServiceOptionsProvider | None = None,
    ) -> None:
        super().__init__()

        self._service_provider = service_provider
        self._options = options

    async def get_next_ai_messages(self, chat: 'mc.Chat') -> 'mc.Chat':
        opts = self._options() if self._options is not None else []

        async with self._service_provider.provide_backend() as service:
            resp = await service.invoke(mc.ChatChoicesRequest(chat, opts))

        return check.single(resp.v).ms


class ChatChoicesStreamServiceStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            service_provider: ChatChoicesStreamServiceBackendProvider,
            *,
            options: ChatChoicesServiceOptionsProvider | None = None,
    ) -> None:
        super().__init__()

        self._service_provider = service_provider
        self._options = options

    async def get_next_ai_messages_streamed(
            self,
            chat: 'mc.Chat',
            delta_callback: ta.Callable[['mc.AiDelta'], ta.Awaitable[None]] | None = None,
    ) -> mc.AiChat:
        opts = self._options() if self._options is not None else []

        async with self._service_provider.provide_backend() as service:
            joiner = mc.AiChoicesDeltaJoiner()

            async with (await service.invoke(mc.ChatChoicesStreamRequest(chat, opts))).v as st_resp:
                async for o in st_resp:
                    joiner.add(o.choices)

                    choice = check.single(o.choices)

                    for delta in choice.deltas:
                        if delta_callback is not None:
                            await delta_callback(delta)

        return check.single(joiner.build())
