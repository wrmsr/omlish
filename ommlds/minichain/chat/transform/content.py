"""
FIXME:
 - replace ..content with this
"""
import typing as ta

from omlish import dataclasses as dc

from ...content.transform.types import ContentTransform
from ..messages import AiMessage
from ..messages import Message
from ..messages import SystemMessage
from ..messages import ToolUseResultMessage
from ..messages import UserMessage
from .visitors import VisitorMessageTransform


C = ta.TypeVar('C')

MessageT = ta.TypeVar('MessageT', bound=Message)


##


@dc.dataclass(frozen=True)
class ContentTransformMessageTransform(VisitorMessageTransform[C]):
    ct: ContentTransform[C]

    def visit_user_message(self, m: UserMessage, ctx: C) -> UserMessage:
        return m.replace(c=self.ct.transform(m.c, ctx))

    def visit_system_message(self, m: SystemMessage, ctx: C) -> SystemMessage:
        return m.replace(c=self.ct.transform(m.c, ctx))

    def visit_tool_use_result_message(self, m: ToolUseResultMessage, ctx: C) -> ToolUseResultMessage:
        if (nc := self.ct.transform(m.tur.c, ctx)) is m.tur.c:
            return m
        return m.replace(tur=dc.replace(m.tur, c=nc))

    def visit_ai_message(self, m: AiMessage, ctx: C) -> AiMessage:
        return m.replace(c=self.ct.transform(m.c, ctx))


def transform_message_content(ct: ContentTransform[C], m: MessageT, ctx: C) -> MessageT:
    return ta.cast(MessageT, ContentTransformMessageTransform(ct).transform(m, ctx))
