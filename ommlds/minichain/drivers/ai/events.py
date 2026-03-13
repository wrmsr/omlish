import typing as ta

from ...chat.messages import Chat
from ...chat.stream.types import AiDelta
from ..events.manager import EventsManager
from ..events.types import AiMessagesEvent
from ..events.types import AiStreamBeginEvent
from ..events.types import AiStreamDeltaEvent
from ..events.types import AiStreamEndEvent
from .types import AiChatGenerator
from .types import GenerateAiChatArgs
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

    async def generate_ai_chat(self, args: GenerateAiChatArgs) -> Chat:
        out = await self._wrapped.generate_ai_chat(args)

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

    async def generate_ai_chat_streamed(
            self,
            args: GenerateAiChatArgs,
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
            out = await self._wrapped.generate_ai_chat_streamed(args, delta_callback=inner)

        finally:
            if sent_begin_event:
                await self._events.emit_event(AiStreamEndEvent())

        await self._events.emit_event(AiMessagesEvent(out, streamed=True))

        return out
