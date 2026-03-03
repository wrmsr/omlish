import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..messages import Chat
from .messages import MessageTransform


C = ta.TypeVar('C')


##


class ChatTransform(lang.Abstract, ta.Generic[C]):
    @abc.abstractmethod
    def transform(self, chat: Chat, ctx: C) -> Chat:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class CompositeChatTransform(ChatTransform[C]):
    cts: ta.Sequence[ChatTransform]

    def transform(self, chat: Chat, ctx: C) -> Chat:
        for ct in self.cts:
            chat = ct.transform(chat, ctx)
        return chat


@dc.dataclass(frozen=True)
class FnChatTransform(ChatTransform[C]):
    fn: ta.Callable[[Chat], Chat]

    def transform(self, chat: Chat, ctx: C) -> Chat:
        return self.fn(chat)


##


@dc.dataclass(frozen=True)
class MessageTransformChatTransform(ChatTransform[C]):
    mt: MessageTransform[C]

    def transform(self, chat: Chat, ctx: C) -> Chat:
        return [o for i in chat for o in self.mt.transform(i, ctx)]


@dc.dataclass(frozen=True)
class LastMessageTransformChatTransform(ChatTransform[C]):
    mt: MessageTransform[C]

    def transform(self, chat: Chat, ctx: C) -> Chat:
        if chat:
            return [*chat[:-1], *self.mt.transform(chat[-1], ctx)]
        else:
            return []
