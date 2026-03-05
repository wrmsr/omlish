import typing as ta

from omlish import lang

from ..messages import Message
from ..visitors import MessageVisitor
from .messages import MessageTransform


##


class VisitorMessageTransform(MessageVisitor[None, Message], MessageTransform, lang.Abstract):
    @ta.final
    def transform(self, m: Message) -> ta.Sequence[Message]:
        """Final - must be identical to `visit`."""

        return [self.visit(m, None)]
