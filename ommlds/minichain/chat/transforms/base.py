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
class CompositeMessageTransform(MessageTransform):
    mts: ta.Sequence[MessageTransform]

    def transform_message(self, message: Message) -> Message:
        for mt in self.mts:
            message = mt.transform_message(message)
        return message


@dc.dataclass(frozen=True)
class FnMessageTransform(MessageTransform, ta.Generic[MessageT]):
    fn: ta.Callable[[MessageT], MessageT]

    def transform_message(self, message: MessageT) -> MessageT:
        return self.fn(message)


@dc.dataclass(frozen=True)
class TypeFilteredMessageTransform(MessageTransform[Message], ta.Generic[MessageT]):
    ty: type | tuple[type, ...]
    mt: MessageTransform[MessageT]

    def transform_message(self, message: Message) -> Message:
        if isinstance(message, self.ty):
            return self.mt.transform_message(ta.cast(MessageT, message))
        else:
            return message


@ta.overload
def fn_message_transform(
        fn: ta.Callable[[MessageT], MessageT],
        ty: type[MessageT],
) -> MessageTransform[MessageT]:
    ...


@ta.overload
def fn_message_transform(
        fn: ta.Callable[[Message], Message],
        ty: type | tuple[type, ...] | None = None,
) -> MessageTransform:
    ...


def fn_message_transform(fn, ty=None) -> MessageTransform[MessageT]:
    mt: MessageTransform = FnMessageTransform(fn)
    if ty is not None:
        mt = TypeFilteredMessageTransform(ty, mt)
    return mt


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
        return [self.mt.transform_message(m) for m in chat]


@dc.dataclass(frozen=True)
class LastMessageTransformChatTransform(ChatTransform):
    mt: MessageTransform

    def transform_chat(self, chat: Chat) -> Chat:
        if chat:
            return [*chat[:-1], self.mt.transform_message(chat[-1])]
        else:
            return []
