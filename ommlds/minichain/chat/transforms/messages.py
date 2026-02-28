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
