"""
Mirrors omlish.funcs.pairs.

TODO:
 - MessagesTransform ? MessageTransformMessagesTransform? :| ...
"""
import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..messages import AnyAiMessage
from ..messages import AnyUserMessage
from ..messages import Chat
from ..messages import Message


MessageF = ta.TypeVar('MessageF', bound=Message)
MessageT = ta.TypeVar('MessageT', bound=Message)


##


class MessageTransform(lang.Abstract, ta.Generic[MessageF, MessageT]):
    @abc.abstractmethod
    def transform_message(self, message: MessageF) -> ta.Sequence[MessageT]:
        raise NotImplementedError


AiMessageTransform: ta.TypeAlias = MessageTransform[AnyAiMessage, AnyAiMessage]
UserMessageTransform: ta.TypeAlias = MessageTransform[AnyUserMessage, AnyUserMessage]


@dc.dataclass(frozen=True)
class CompositeMessageTransform(MessageTransform):
    mts: ta.Sequence[MessageTransform]

    def transform_message(self, message: Message) -> Chat:
        chat: Chat = [message]
        for mt in self.mts:
            chat = [o for i in chat for o in mt.transform_message(i)]
        return chat


@dc.dataclass(frozen=True)
class FnMessageTransform(MessageTransform, ta.Generic[MessageF, MessageT]):
    fn: ta.Callable[[MessageF], ta.Sequence[MessageT]]

    def transform_message(self, message: MessageF) -> ta.Sequence[MessageT]:
        return self.fn(message)


@dc.dataclass(frozen=True)
class TypeFilteredMessageTransform(MessageTransform, ta.Generic[MessageF, MessageT]):
    ty: type | tuple[type, ...]
    mt: MessageTransform[MessageF, MessageT]

    def transform_message(self, message: Message) -> Chat:
        if isinstance(message, self.ty):
            return self.mt.transform_message(ta.cast(MessageF, message))
        else:
            return [message]


##


class ChatTransform(lang.Abstract):
    @abc.abstractmethod
    def transform_chat(self, chat: Chat) -> Chat:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class CompositeChatTransform(ChatTransform):
    cts: ta.Sequence[ChatTransform]

    def transform_chat(self, chat: Chat) -> Chat:
        for ct in self.cts:
            chat = ct.transform_chat(chat)
        return chat


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
        return [o for i in chat for o in self.mt.transform_message(i)]


@dc.dataclass(frozen=True)
class LastMessageTransformChatTransform(ChatTransform):
    mt: MessageTransform

    def transform_chat(self, chat: Chat) -> Chat:
        if chat:
            return [*chat[:-1], *self.mt.transform_message(chat[-1])]
        else:
            return []
