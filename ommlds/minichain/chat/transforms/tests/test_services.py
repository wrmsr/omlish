from omlish import check
from omlish import dataclasses as dc

from ...messages import AiMessage
from ...messages import UserMessage
from ...services import ChatRequest
from ...services import ChatResponse
from ...services import static_check_is_chat_service
from ..base import FnMessageTransform
from ..services import ResponseMessageTransformingChatService


@static_check_is_chat_service
class DummyChatService:
    def invoke(self, request: ChatRequest) -> ChatResponse:
        um = check.isinstance(request.v[-1], UserMessage)
        return ChatResponse(AiMessage(check.isinstance(um.c, str) + '!'))


def test_response_message_transforming_chat_service():
    dcs = DummyChatService()
    print(dcs.invoke(ChatRequest([UserMessage('hi')])))

    tcs = ResponseMessageTransformingChatService(
        FnMessageTransform(lambda m: dc.replace(m, c=check.isinstance(m.c, str) + '?')),  # type: ignore[attr-defined]
        dcs,
    )
    print(tcs.invoke(ChatRequest([UserMessage('hi')])))
