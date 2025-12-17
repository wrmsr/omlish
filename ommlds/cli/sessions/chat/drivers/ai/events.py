import typing as ta

from ...... import minichain as mc
from ..events.manager import ChatEventsManager
from ..events.types import AiDeltaChatEvent
from ..events.types import AiMessagesChatEvent
from .types import AiChatGenerator
from .types import StreamAiChatGenerator


##


class EventEmittingAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: AiChatGenerator,
            events: ChatEventsManager,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._events = events

    async def get_next_ai_messages(self, chat: 'mc.Chat') -> 'mc.Chat':
        out = await self._wrapped.get_next_ai_messages(chat)

        await self._events.emit_event(AiMessagesChatEvent(out))

        return out


class EventEmittingStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: StreamAiChatGenerator,
            events: ChatEventsManager,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._events = events

    async def get_next_ai_messages_streamed(
            self,
            chat: 'mc.Chat',
            delta_callback: ta.Callable[['mc.AiDelta'], ta.Awaitable[None]] | None = None,
    ) -> 'mc.Chat':
        async def inner(delta: mc.AiDelta) -> None:
            await self._events.emit_event(AiDeltaChatEvent(delta))

            if delta_callback is not None:
                await delta_callback(delta)

        return await self._wrapped.get_next_ai_messages_streamed(chat, delta_callback=inner)
