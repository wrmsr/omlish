import typing as ta

from omlish import check
from omlish import lang

from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesService
from ...chat.choices.stream.joining import AiChoicesDeltaJoiner
from ...chat.choices.stream.services import ChatChoicesStreamRequest
from ...chat.choices.stream.services import ChatChoicesStreamService
from ...chat.choices.types import ChatChoicesOptions
from ...chat.messages import AiChat
from ...chat.messages import Chat
from ...chat.stream.types import AiDelta
from .types import AiChatGenerator
from .types import StreamAiChatGenerator


##


class ChatChoicesServiceOptionsProvider(lang.Func0[ta.Sequence[ChatChoicesOptions]]):
    pass


ChatChoicesServiceOptionsProviders = ta.NewType('ChatChoicesServiceOptionsProviders', ta.Sequence[ChatChoicesServiceOptionsProvider])  # noqa


##


class ChatChoicesServiceAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            service: ChatChoicesService,
            *,
            options: ChatChoicesServiceOptionsProvider | None = None,
    ) -> None:
        super().__init__()

        self._service = service
        self._options = options

    async def get_next_ai_messages(self, chat: Chat) -> Chat:
        opts = self._options() if self._options is not None else []

        resp = await self._service.invoke(ChatChoicesRequest(chat, opts))

        return check.single(resp.v).ms


class ChatChoicesStreamServiceStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            service: ChatChoicesStreamService,
            *,
            options: ChatChoicesServiceOptionsProvider | None = None,
    ) -> None:
        super().__init__()

        self._service = service
        self._options = options

    async def get_next_ai_messages_streamed(
            self,
            chat: Chat,
            delta_callback: ta.Callable[[AiDelta], ta.Awaitable[None]] | None = None,
    ) -> AiChat:
        opts = self._options() if self._options is not None else []

        joiner = AiChoicesDeltaJoiner()

        async with (await self._service.invoke(ChatChoicesStreamRequest(chat, opts))).v as st_resp:
            async for o in st_resp:
                joiner.add(o.choices)

                choice = check.single(o.choices)

                for delta in choice.deltas:
                    if delta_callback is not None:
                        await delta_callback(delta)

        return check.single(joiner.build())
