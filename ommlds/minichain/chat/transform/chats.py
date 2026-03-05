import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..messages import Chat
from .messages import MessageTransform


##


class ChatTransform(lang.Abstract):
    @abc.abstractmethod
    def transform(self, chat: Chat) -> Chat:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class CompositeChatTransform(ChatTransform):
    cts: ta.Sequence[ChatTransform]

    def transform(self, chat: Chat) -> Chat:
        for ct in self.cts:
            chat = ct.transform(chat)
        return chat


@dc.dataclass(frozen=True)
class FnChatTransform(ChatTransform):
    fn: ta.Callable[[Chat], Chat]

    def transform(self, chat: Chat) -> Chat:
        return self.fn(chat)


##


@dc.dataclass(frozen=True)
class MessageTransformChatTransform(ChatTransform):
    mt: MessageTransform

    def transform(self, chat: Chat) -> Chat:
        return [o for i in chat for o in self.mt.transform(i)]


@dc.dataclass(frozen=True)
class LastMessageTransformChatTransform(ChatTransform):
    mt: MessageTransform

    def transform(self, chat: Chat) -> Chat:
        if chat:
            return [*chat[:-1], *self.mt.transform(chat[-1])]
        else:
            return []
