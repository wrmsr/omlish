import typing as ta

from omlish import lang

from ..messages import Message
from ..visitors import MessageVisitor
from .messages import MessageTransform


C = ta.TypeVar('C')


##


class VisitorMessageTransform(MessageVisitor[C, Message], MessageTransform[C], lang.Abstract):
    @ta.final
    def transform(self, message: Message, ctx: C) -> ta.Sequence[Message]:
        """Final - must be identical to `visit`."""

        return [self.visit(message, ctx)]
