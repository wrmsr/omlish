import abc

from omlish import dataclasses as dc
from omlish import lang

from ..messages import Chat
from ..messages import Message


##


class MessageTransform(lang.Abstract):
    @abc.abstractmethod
    def transform_message(self, message: Message) -> Message:
        raise NotImplementedError


##


class ChatTransform(lang.Abstract):
    @abc.abstractmethod
    def transform_chat(self, chat: Chat) -> Chat:
        raise NotImplementedError


#


@dc.dataclass(frozen=True)
class MessageTransformChatTransform(ChatTransform):
    inner: MessageTransform

    def transform_chat(self, chat: Chat) -> Chat:
        return [self.inner.transform_message(m) for m in chat]
