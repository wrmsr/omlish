import typing as ta

from ...chat.messages import Chat
from ...chat.stream.types import AiDelta
from ...chat.transform.chats import ChatTransform
from .types import AiChatGenerator
from .types import GenerateAiChatArgs
from .types import StreamAiChatGenerator


##


AiChatChatTransform = ta.TypeVar('AiChatChatTransform', bound=ChatTransform)


class ChatTransformAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            transform: AiChatChatTransform,
            *,
            wrapped: AiChatGenerator,
    ) -> None:
        super().__init__()

        self._transform = transform
        self._wrapped = wrapped

    async def generate_ai_chat(self, args: GenerateAiChatArgs) -> Chat:
        out = await self._wrapped.generate_ai_chat(args)

        out = self._transform.transform(out)

        return out


class ChatTransformStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            transform: AiChatChatTransform,
            *,
            wrapped: StreamAiChatGenerator,
    ) -> None:
        super().__init__()

        self._transform = transform
        self._wrapped = wrapped

    async def generate_ai_chat_streamed(
            self,
            args: GenerateAiChatArgs,
            delta_callback: ta.Callable[[AiDelta], ta.Awaitable[None]] | None = None,
    ) -> Chat:
        out = await self._wrapped.generate_ai_chat_streamed(args, delta_callback=delta_callback)

        out = self._transform.transform(out)

        return out
