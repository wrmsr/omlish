import asyncio
import typing as ta

from omlish.asyncs.asyncio import all as au

from ...chat.messages import Chat
from ...chat.stream.types import AiDelta
from ..events.manager import EventsManager
from .events import AiMessagesEvent
from .events import AiStreamBeginEvent
from .events import AiStreamDeltaEvent
from .events import AiStreamEndEvent
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

        await self._events.emit_event(AiMessagesEvent(out, message_uuid=args.message_uuid))

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
        end_exception: BaseException | None = None

        async def inner(delta: AiDelta) -> None:
            nonlocal sent_begin_event
            if not sent_begin_event:
                await self._events.emit_event(AiStreamBeginEvent(message_uuid=args.message_uuid))
                sent_begin_event = True

            await self._events.emit_event(AiStreamDeltaEvent(delta, message_uuid=args.message_uuid))

            if delta_callback is not None:
                await delta_callback(delta)

        async def emit_end() -> None:
            if sent_begin_event:
                await self._events.emit_event(AiStreamEndEvent(message_uuid=args.message_uuid, exception=end_exception))

        async with au.shielded_finally(emit_end):
            try:
                out = await self._wrapped.generate_ai_chat_streamed(args, delta_callback=inner)
            except (Exception, asyncio.CancelledError) as e:
                end_exception = e
                raise

        await self._events.emit_event(AiMessagesEvent(out, streamed=True, message_uuid=args.message_uuid))

        return out
