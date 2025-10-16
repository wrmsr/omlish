import typing as ta

from ...... import minichain as mc
from ...content.messages import MessageContentExtractor
from ...rendering.types import ContentRendering
from .types import AiChatGenerator
from .types import StreamAiChatGenerator


##


class RenderingAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: AiChatGenerator,
            extractor: MessageContentExtractor,
            renderer: ContentRendering,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._extractor = extractor
        self._renderer = renderer

    async def get_next_ai_messages(self, chat: mc.Chat) -> mc.AiChat:
        out = await self._wrapped.get_next_ai_messages(chat)

        # FIXME: render lol

        return out


class RenderingStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: StreamAiChatGenerator,
            extractor: MessageContentExtractor,
            renderer: ContentRendering,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._extractor = extractor
        self._renderer = renderer

    async def get_next_ai_messages_streamed(
            self,
            chat: mc.Chat,
            delta_callback: ta.Callable[[mc.AiChoiceDelta], ta.Awaitable[None]] | None = None,
    ) -> mc.AiChat:
        async def inner(delta: mc.AiChoiceDelta) -> None:
            # FIXME: render lol

            if delta_callback is not None:
                await delta_callback(delta)

        return await self._wrapped.get_next_ai_messages_streamed(chat, delta_callback=inner)
