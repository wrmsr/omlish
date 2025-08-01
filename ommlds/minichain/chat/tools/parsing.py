
from omlish import check
from omlish import dataclasses as dc

from ...text.toolparsing.base import ParsedToolExec
from ...text.toolparsing.base import ToolExecParser
from ..messages import AiMessage
from ..messages import ToolExecRequest
from ..transforms.base import MessageTransform


##


@dc.dataclass(frozen=True)
class ToolExecParsingMessageTransform(MessageTransform[AiMessage]):
    parser: ToolExecParser

    def transform_message(self, message: AiMessage) -> AiMessage:
        pts = self.parser.parse_tool_execs_(check.isinstance(message.c or '', str))

        sl: list[str] = []
        xl: list[ToolExecRequest] = []
        for pt in pts:
            if isinstance(pt, ParsedToolExec):
                xl.append(ToolExecRequest(
                    id=pt.id,
                    name=pt.name,
                    args=pt.args,
                ))

            elif isinstance(pt, str):
                sl.append(pt)

            else:
                raise TypeError(pt)

        return dc.replace(
            message,
            c=sl or None,
            tool_exec_requests=[
                *(message.tool_exec_requests or []),
                *xl,
            ],
        )
