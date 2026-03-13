import abc
import typing as ta

from omlish import lang

from ...chat.messages import Chat
from ...chat.stream.types import AiDelta


##


class AiChatGenerator(lang.Abstract):
    @abc.abstractmethod
    def get_next_ai_messages(self, chat: Chat) -> ta.Awaitable[Chat]:
        raise NotImplementedError


class StreamAiChatGenerator(AiChatGenerator, lang.Abstract):
    def get_next_ai_messages(self, chat: Chat) -> ta.Awaitable[Chat]:
        return self.get_next_ai_messages_streamed(chat)

    @abc.abstractmethod
    def get_next_ai_messages_streamed(
            self,
            chat: Chat,
            delta_callback: ta.Callable[[AiDelta], ta.Awaitable[None]] | None = None,
    ) -> ta.Awaitable[Chat]:
        raise NotImplementedError
