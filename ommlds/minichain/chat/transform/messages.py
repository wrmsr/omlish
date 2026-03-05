import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..messages import Chat
from ..messages import Message


##


class MessageTransform(lang.Abstract):
    @abc.abstractmethod
    def transform(self, m: Message) -> ta.Sequence[Message]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class CompositeMessageTransform(MessageTransform):
    mts: ta.Sequence[MessageTransform]

    def transform(self, m: Message) -> Chat:
        chat: Chat = [m]
        for mt in self.mts:
            chat = [o for i in chat for o in mt.transform(i)]
        return chat


@dc.dataclass(frozen=True)
class FnMessageTransform(MessageTransform):
    fn: ta.Callable[[Message], ta.Sequence[Message]]

    def transform(self, m: Message) -> ta.Sequence[Message]:
        return self.fn(m)


@dc.dataclass(frozen=True)
class TypeFilteredMessageTransform(MessageTransform):
    ty: type | tuple[type, ...]
    mt: MessageTransform

    def transform(self, m: Message) -> Chat:
        if isinstance(m, self.ty):
            return self.mt.transform(m)
        else:
            return [m]
