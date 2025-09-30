from omlish import dataclasses as dc

from ..messages import check_ai_chat
from ..services import ChatRequest
from ..services import ChatResponse
from ..services import ChatService
from ..services import static_check_is_chat_service
from .base import ChatTransform


##


@static_check_is_chat_service
@dc.dataclass(frozen=True)
class RequestChatTransformingChatService:
    ct: ChatTransform
    svc: ChatService

    async def invoke(self, request: ChatRequest) -> ChatResponse:
        new_chat = self.ct.transform_chat(request.v)
        new_req = dc.replace(request, v=new_chat)
        return await self.svc.invoke(new_req)


#


@static_check_is_chat_service
@dc.dataclass(frozen=True)
class ResponseChatTransformingChatService:
    ct: ChatTransform
    svc: ChatService

    async def invoke(self, request: ChatRequest) -> ChatResponse:
        orig_resp = await self.svc.invoke(request)
        new_chat = check_ai_chat(self.ct.transform_chat(orig_resp.v))
        return dc.replace(orig_resp, v=new_chat)
