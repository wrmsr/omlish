from omlish import check
from omlish import dataclasses as dc

from ...services import Response
from ..messages import AiChat
from ..services import ChatRequest
from ..services import static_check_is_chat_service
from .services import ChatChoicesService
from .types import ChatChoicesOutputs


##


@static_check_is_chat_service
@dc.dataclass(frozen=True)
class ChatChoicesServiceChatService:
    service: ChatChoicesService

    async def invoke(self, request: ChatRequest) -> Response[AiChat, ChatChoicesOutputs]:
        resp = await self.service.invoke(request)
        return Response(check.single(resp.v).ms, resp.outputs)
