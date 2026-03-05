import typing as ta

from omlish import check
from omlish import dataclasses as dc

from ...text.toolparsing.base import ParsedToolExec
from ...text.toolparsing.base import ToolExecParser
from ..messages import AiMessage
from ..messages import AnyAiMessage
from ..messages import Message
from ..messages import ToolUse
from ..messages import ToolUseMessage
from ..transform.messages import MessageTransform


##


@dc.dataclass(frozen=True)
class ToolExecParsingMessageTransform(MessageTransform):
    parser: ToolExecParser

    def transform(self, message: Message) -> ta.Sequence[Message]:
        if not isinstance(message, AiMessage):
            return [message]

        pts = self.parser.parse_tool_execs_(check.isinstance(message.c or '', str))

        out: list[AnyAiMessage] = []

        for pt in pts:
            if isinstance(pt, ParsedToolExec):
                out.append(ToolUseMessage(ToolUse(
                    id=pt.id,
                    name=pt.name,
                    args=pt.args,
                    raw_args=pt.raw_body,
                )))

            elif isinstance(pt, str):
                out.append(AiMessage(pt))

            else:
                raise TypeError(pt)

        return out
