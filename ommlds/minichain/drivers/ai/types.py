import abc
import typing as ta
import uuid as uuid_

from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import Chat
from ...chat.stream.types import AiDelta


##


@dc.dataclass(frozen=True)
class GenerateAiChatArgs:
    chat: Chat

    _: dc.KW_ONLY

    message_uuid: uuid_.UUID | None = None


class AiChatGenerator(lang.Abstract):
    @abc.abstractmethod
    def generate_ai_chat(self, args: GenerateAiChatArgs) -> ta.Awaitable[Chat]:
        raise NotImplementedError


class StreamAiChatGenerator(AiChatGenerator, lang.Abstract):
    def generate_ai_chat(self, args: GenerateAiChatArgs) -> ta.Awaitable[Chat]:
        return self.generate_ai_chat_streamed(args)

    @abc.abstractmethod
    def generate_ai_chat_streamed(
            self,
            args: GenerateAiChatArgs,
            delta_callback: ta.Callable[[AiDelta], ta.Awaitable[None]] | None = None,
    ) -> ta.Awaitable[Chat]:
        raise NotImplementedError
