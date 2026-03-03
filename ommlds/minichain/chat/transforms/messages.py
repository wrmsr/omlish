import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..messages import Chat
from ..messages import Message


C = ta.TypeVar('C')


##


class MessageTransform(lang.Abstract, ta.Generic[C]):
    @abc.abstractmethod
    def transform(self, message: Message, ctx: C) -> ta.Sequence[Message]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class CompositeMessageTransform(MessageTransform[C]):
    mts: ta.Sequence[MessageTransform[C]]

    def transform(self, message: Message, ctx: C) -> Chat:
        chat: Chat = [message]
        for mt in self.mts:
            chat = [o for i in chat for o in mt.transform(i, ctx)]
        return chat


@dc.dataclass(frozen=True)
class FnMessageTransform(MessageTransform[C]):
    fn: ta.Callable[[Message], ta.Sequence[Message]]

    def transform(self, message: Message, ctx: C) -> ta.Sequence[Message]:
        return self.fn(message)


@dc.dataclass(frozen=True)
class TypeFilteredMessageTransform(MessageTransform[C]):
    ty: type | tuple[type, ...]
    mt: MessageTransform[C]

    def transform(self, message: Message, ctx: C) -> Chat:
        if isinstance(message, self.ty):
            return self.mt.transform(message, ctx)
        else:
            return [message]
