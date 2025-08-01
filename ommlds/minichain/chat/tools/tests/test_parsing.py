from omlish import check
from omlish import dataclasses as dc

from ....text.toolparsing.dumb import DumbToolExecParser
from ...messages import AiMessage
from ...messages import UserMessage
from ...services import ChatRequest
from ...services import ChatResponse
from ...services import static_check_is_chat_service
from ...transforms.services import ResponseMessageTransformingChatService
from ..parsing import ToolExecParsingMessageTransform


@static_check_is_chat_service
@dc.dataclass(frozen=True, kw_only=True)
class DummyChatService:
    prefix: str = ''
    suffix: str = ''

    def invoke(self, request: ChatRequest) -> ChatResponse:
        um = check.isinstance(request.v[-1], UserMessage)
        return ChatResponse(AiMessage(''.join([self.prefix, check.isinstance(um.c, str), self.suffix])))


TOOL_RESPONSE = """\
<tools>
{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}
</tools>\
"""


def test_response_message_transforming_chat_service():
    dcs = DummyChatService(prefix=TOOL_RESPONSE + '\n')
    print(dcs.invoke(ChatRequest([UserMessage('hi')])))

    tcs = ResponseMessageTransformingChatService(
        ToolExecParsingMessageTransform(
            DumbToolExecParser(
                '<tools>',
                '</tools>',
                strip_whitespace=True,
            ),
        ),
        dcs,
    )
    print(tcs.invoke(ChatRequest([UserMessage('hi')])))
