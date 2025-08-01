from omlish import check
from omlish import dataclasses as dc

from ..messages import AiMessage
from ..services import ChatRequest
from ..services import ChatResponse
from ..services import ChatService
from ..services import static_check_is_chat_service
from .base import ChatTransform
from .base import MessageTransform


##


@static_check_is_chat_service
@dc.dataclass(frozen=True)
class RequestChatTransformingChatService:
    ct: ChatTransform
    svc: ChatService

    def invoke(self, request: ChatRequest) -> ChatResponse:
        new_chat = self.ct.transform_chat(request.v)
        new_req = dc.replace(request, v=new_chat)
        return self.svc.invoke(new_req)


#


@static_check_is_chat_service
@dc.dataclass(frozen=True)
class ResponseMessageTransformingChatService:
    mt: MessageTransform[AiMessage]
    svc: ChatService

    def invoke(self, request: ChatRequest) -> ChatResponse:
        orig_resp = self.svc.invoke(request)
        new_msg = self.mt.transform_message(orig_resp.v)
        return dc.replace(orig_resp, v=check.isinstance(new_msg, AiMessage))
