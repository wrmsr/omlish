import abc
import typing as ta

from omlish import lang

from ...... import minichain as mc


##


class AiChatGenerator(lang.Abstract):
    @abc.abstractmethod
    def get_next_ai_messages(self, chat: 'mc.Chat') -> ta.Awaitable['mc.Chat']:
        raise NotImplementedError


class StreamAiChatGenerator(AiChatGenerator, lang.Abstract):
    def get_next_ai_messages(self, chat: 'mc.Chat') -> ta.Awaitable['mc.Chat']:
        return self.get_next_ai_messages_streamed(chat)

    @abc.abstractmethod
    def get_next_ai_messages_streamed(
            self,
            chat: 'mc.Chat',
            delta_callback: ta.Callable[['mc.AiDelta'], ta.Awaitable[None]] | None = None,
    ) -> ta.Awaitable['mc.Chat']:
        raise NotImplementedError
