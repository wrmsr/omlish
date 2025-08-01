import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..messages import Chat
from ..messages import Message


MessageT = ta.TypeVar('MessageT', bound=Message)


##


class MessageTransform(lang.Abstract, ta.Generic[MessageT]):
    @abc.abstractmethod
    def transform_message(self, message: MessageT) -> MessageT:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class FnMessageTransform(MessageTransform, ta.Generic[MessageT]):
    fn: ta.Callable[[MessageT], MessageT]

    def transform_message(self, message: MessageT) -> MessageT:
        return self.fn(message)


##


class ChatTransform(lang.Abstract):
    @abc.abstractmethod
    def transform_chat(self, chat: Chat) -> Chat:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class FnChatTransform(ChatTransform):
    fn: ta.Callable[[Chat], Chat]

    def transform_chat(self, chat: Chat) -> Chat:
        return self.fn(chat)


#


@dc.dataclass(frozen=True)
class MessageTransformChatTransform(ChatTransform):
    mt: MessageTransform

    def transform_chat(self, chat: Chat) -> Chat:
        return [self.mt.transform_message(m) for m in chat]


@dc.dataclass(frozen=True)
class LastMessageTransformChatTransform(ChatTransform):
    mt: MessageTransform

    def transform_chat(self, chat: Chat) -> Chat:
        if chat:
            return [*chat[:-1], self.mt.transform_message(chat[-1])]
        else:
            return []
