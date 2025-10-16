from omlish import check

from ...... import minichain as mc
from .types import AiChatGenerator
from .types import AiChoiceDeltaCallback


##


class ChatChoicesServiceAiChatGenerator(AiChatGenerator):
    def __init__(self, service: mc.ChatChoicesService) -> None:
        super().__init__()

        self._service = service

    async def get_next_ai_messages(self, chat: mc.Chat) -> mc.AiChat:
        resp = await self._service.invoke(mc.ChatChoicesRequest(chat))

        return check.single(resp.v).ms


class ChatChoicesStreamServiceAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            service: mc.ChatChoicesStreamService,
            *,
            on_delta: AiChoiceDeltaCallback | None = None,
    ) -> None:
        super().__init__()

        self._service = service
        self._on_delta = on_delta

    async def get_next_ai_messages(self, chat: mc.Chat) -> mc.AiChat:
        lst: list[str] = []

        async with (await self._service.invoke(mc.ChatChoicesStreamRequest(chat))).v as st_resp:
            async for o in st_resp:
                choice = check.single(o.choices)

                for delta in choice.deltas:
                    if self._on_delta is not None:
                        await self._on_delta(delta)

                c = check.isinstance(delta, mc.ContentAiChoiceDelta).c  # noqa
                if c is not None:
                    lst.append(check.isinstance(c, str))

        return [mc.AiMessage(''.join(lst))]
