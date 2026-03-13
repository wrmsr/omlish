import typing as ta

from ...chat.messages import Chat
from ...chat.stream.types import AiDelta
from ..events.manager import EventsManager
from ..events.types import AiMessagesEvent
from ..events.types import AiStreamBeginEvent
from ..events.types import AiStreamDeltaEvent
from ..events.types import AiStreamEndEvent
from .types import AiChatGenerator
from .types import StreamAiChatGenerator


##


class EventEmittingAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: AiChatGenerator,
            events: EventsManager,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._events = events

    async def get_next_ai_messages(self, chat: Chat) -> Chat:
        out = await self._wrapped.get_next_ai_messages(chat)

        await self._events.emit_event(AiMessagesEvent(out))

        return out


class EventEmittingStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: StreamAiChatGenerator,
            events: EventsManager,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._events = events

    async def get_next_ai_messages_streamed(
            self,
            chat: Chat,
            delta_callback: ta.Callable[[AiDelta], ta.Awaitable[None]] | None = None,
    ) -> Chat:
        sent_begin_event = False

        async def inner(delta: AiDelta) -> None:
            nonlocal sent_begin_event
            if not sent_begin_event:
                await self._events.emit_event(AiStreamBeginEvent())
                sent_begin_event = True

            await self._events.emit_event(AiStreamDeltaEvent(delta))

            if delta_callback is not None:
                await delta_callback(delta)

        try:
            out = await self._wrapped.get_next_ai_messages_streamed(chat, delta_callback=inner)

        finally:
            if sent_begin_event:
                await self._events.emit_event(AiStreamEndEvent())

        await self._events.emit_event(AiMessagesEvent(out, streamed=True))

        return out
