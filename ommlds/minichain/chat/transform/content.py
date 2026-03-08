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


MessageT = ta.TypeVar('MessageT', bound=Message)


##


@dc.dataclass(frozen=True)
class ContentTransformMessageTransform(VisitorMessageTransform):
    ct: ContentTransform

    def visit_system_message(self, m: SystemMessage, ctx: None) -> SystemMessage:
        return m.replace(c=self.ct.transform(m.c))

    def visit_user_message(self, m: UserMessage, ctx: None) -> UserMessage:
        return m.replace(c=self.ct.transform(m.c))

    def visit_tool_use_result_message(self, m: ToolUseResultMessage, ctx: None) -> ToolUseResultMessage:
        if (nc := self.ct.transform(m.tur.c)) is m.tur.c:
            return m
        return m.replace(tur=dc.replace(m.tur, c=nc))

    def visit_ai_message(self, m: AiMessage, ctx: None) -> AiMessage:
        return m.replace(c=self.ct.transform(m.c))


def transform_message_content(ct: ContentTransform, m: MessageT) -> MessageT:
    return ta.cast(MessageT, ContentTransformMessageTransform(ct).transform(m))
