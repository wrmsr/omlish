import abc

from omlish import dataclasses as dc
from omlish import lang

from ...transform.sequence import CompositeSequenceTransform
from ...transform.sequence import FnSequenceTransform
from ...transform.sequence import SequenceTransform
from ...transform.sequence import GeneralTransformSequenceTransform
from ..messages import Chat
from ..messages import Message
from .messages import MessageTransform


##


class ChatTransform(SequenceTransform[Message], lang.Abstract):
    @abc.abstractmethod
    def transform(self, chat: Chat) -> Chat:
        raise NotImplementedError


#


class CompositeChatTransform(CompositeSequenceTransform[Message], ChatTransform):
    pass


class FnChatTransform(FnSequenceTransform[Message], ChatTransform):
    pass


class MessageTransformChatTransform(GeneralTransformSequenceTransform[Message], ChatTransform):
    pass


##


@dc.dataclass(frozen=True)
class LastMessageTransformChatTransform(ChatTransform):
    mt: MessageTransform

    def transform(self, chat: Chat) -> Chat:
        if chat:
            return [*chat[:-1], *self.mt.transform(chat[-1])]
        else:
            return []
