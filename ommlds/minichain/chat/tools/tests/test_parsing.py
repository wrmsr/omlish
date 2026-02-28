from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ....text.toolparsing.dumb import DumbToolExecParser
from ...messages import AiMessage
from ...messages import UserMessage
from ...services import ChatRequest
from ...services import ChatResponse
from ...services import static_check_is_chat_service
from ...transforms.chats import MessageTransformChatTransform
from ...transforms.services import ResponseChatTransformingChatService
from ..parsing import ToolExecParsingMessageTransform


@static_check_is_chat_service
@dc.dataclass(frozen=True, kw_only=True)
class DummyChatService:
    prefix: str = ''
    suffix: str = ''

    async def invoke(self, request: ChatRequest) -> ChatResponse:
        um = check.isinstance(request.v[-1], UserMessage)
        return ChatResponse([AiMessage(''.join([self.prefix, check.isinstance(um.c, str), self.suffix]))])


TOOL_RESPONSE = """\
<tools>
{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}
</tools>\
"""


def test_response_message_transforming_chat_service():
    dcs = DummyChatService(prefix=TOOL_RESPONSE + '\n')
    print(lang.sync_await(dcs.invoke(ChatRequest([UserMessage('hi')]))))

    tcs = ResponseChatTransformingChatService(
        MessageTransformChatTransform(
            ToolExecParsingMessageTransform(
                DumbToolExecParser(
                    '<tools>',
                    '</tools>',
                    strip_whitespace=True,
                ),
            ),
        ),
        dcs,
    )
    print(lang.sync_await(tcs.invoke(ChatRequest([UserMessage('hi')]))))
