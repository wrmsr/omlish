import typing as ta

from ...... import minichain as mc
from .....content.messages import MessageContentExtractor
from .....content.messages import MessageContentExtractorImpl
from .....rendering.types import ContentRendering
from .....rendering.types import StreamContentRendering
from .types import AiChatGenerator
from .types import StreamAiChatGenerator


##


class RenderingAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: AiChatGenerator,
            extractor: MessageContentExtractor | None = None,
            renderer: ContentRendering,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        if extractor is None:
            extractor = MessageContentExtractorImpl()
        self._extractor = extractor
        self._renderer = renderer

    async def get_next_ai_messages(self, chat: 'mc.Chat') -> 'mc.Chat':
        out = await self._wrapped.get_next_ai_messages(chat)

        for msg in out:
            if (c := self._extractor.extract_message_content(msg)) is not None:
                await self._renderer.render_content(c)

        return out


class RenderingStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: StreamAiChatGenerator,
            extractor: MessageContentExtractor | None = None,
            renderer: StreamContentRendering,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        if extractor is None:
            extractor = MessageContentExtractorImpl()
        self._extractor = extractor
        self._renderer = renderer

    async def get_next_ai_messages_streamed(
            self,
            chat: 'mc.Chat',
            delta_callback: ta.Callable[['mc.AiDelta'], ta.Awaitable[None]] | None = None,
    ) -> mc.Chat:
        async with self._renderer.create_context() as renderer:
            async def inner(delta: mc.AiDelta) -> None:
                if isinstance(delta, mc.ContentAiDelta):
                    await renderer.render_content(delta.c)

                if delta_callback is not None:
                    await delta_callback(delta)

            return await self._wrapped.get_next_ai_messages_streamed(chat, delta_callback=inner)
