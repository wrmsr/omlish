import abc
import typing as ta

from omlish import check
from omlish import lang
import openai

from .messages import AiMessage
from .messages import Message
from .messages import MessageRole
from .messages import Messages
from .types import StrMap


##


class ChatCompleter(abc.ABC):
    @abc.abstractmethod
    def complete_chat(self, messages: Messages) -> AiMessage:
        raise NotImplementedError


#


class OpenaiChatCompleter(ChatCompleter, lang.Final):
    def __init__(
            self,
            client: openai.OpenAI,
            model: str,
    ) -> None:
        super().__init__()
        self._client = client
        self._model = model

    _ROLE_MAP: ta.ClassVar[ta.Mapping[MessageRole, str]] = {
        MessageRole.SYSTEM: 'system',
        MessageRole.HUMAN: 'user',
        MessageRole.AI: 'assistant',
    }

    def _build_message_payload(self, msg: Message) -> StrMap:
        return dict(
            role=self._ROLE_MAP[msg.role],
            content=msg.content,
        )

    def complete_chat(self, msgs: Messages) -> AiMessage:
        payload = {
            'messages': [self._build_message_payload(msg) for msg in msgs],
            'model': self._model,
            'n': 1,
            'stream': False,
            'temperature': 0.7,
        }

        response = self._client.chat.completions.create(**payload)
        choice = check.single(response.choices)
        return AiMessage(choice.message.content)
