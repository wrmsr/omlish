import typing as ta

from omlish import check

from ...... import minichain as mc
from ...backends.types import ChatChoicesServiceBackendProvider
from .types import AiChatGenerator
from .types import StreamAiChatGenerator


##


ChatChoicesServiceOptions = ta.NewType('ChatChoicesServiceOptions', ta.Sequence[mc.ChatChoicesOptions])


##


class ChatChoicesServiceAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            service_provider: ChatChoicesServiceBackendProvider,
            *,
            options: ChatChoicesServiceOptions | None = None,
    ) -> None:
        super().__init__()

        self._service_provider = service_provider
        self._options = options

    async def get_next_ai_messages(self, chat: mc.Chat) -> mc.AiChat:
        async with self._service_provider.provide_backend() as service:
            resp = await service.invoke(mc.ChatChoicesRequest(chat, self._options or []))

        return check.single(resp.v).ms


class ChatChoicesStreamServiceStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            service: mc.ChatChoicesStreamService,
            *,
            options: ChatChoicesServiceOptions | None = None,
    ) -> None:
        super().__init__()

        self._service = service
        self._options = options

    async def get_next_ai_messages_streamed(
            self,
            chat: mc.Chat,
            delta_callback: ta.Callable[[mc.AiChoiceDelta], ta.Awaitable[None]] | None = None,
    ) -> mc.AiChat:
        lst: list[str] = []

        async with (await self._service.invoke(mc.ChatChoicesStreamRequest(chat, self._options or []))).v as st_resp:
            async for o in st_resp:
                choice = check.single(o.choices)

                for delta in choice.deltas:
                    if delta_callback is not None:
                        await delta_callback(delta)

                c = check.isinstance(delta, mc.ContentAiChoiceDelta).c  # noqa
                if c is not None:
                    lst.append(check.isinstance(c, str))

        return [mc.AiMessage(''.join(lst))]
