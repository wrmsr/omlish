from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...messages import AiMessage
from ...messages import UserMessage
from ...services import ChatRequest
from ...services import ChatResponse
from ...services import static_check_is_chat_service
from ..chats import MessageTransformChatTransform
from ..messages import FnMessageTransform
from ..services import ResponseChatTransformingChatService


@static_check_is_chat_service
class DummyChatService:
    async def invoke(self, request: ChatRequest) -> ChatResponse:
        um = check.isinstance(request.v[-1], UserMessage)
        return ChatResponse([AiMessage(check.isinstance(um.c, str) + '!')])


def test_response_message_transforming_chat_service():
    dcs = DummyChatService()
    print(lang.sync_await(dcs.invoke(ChatRequest([UserMessage('hi')]))))

    tcs = ResponseChatTransformingChatService(
        MessageTransformChatTransform(
            FnMessageTransform(lambda m: [dc.replace(m, c=check.isinstance(m.c, str) + '?')]),
        ),
        dcs,
    )
    print(lang.sync_await(tcs.invoke(ChatRequest([UserMessage('hi')]))))
