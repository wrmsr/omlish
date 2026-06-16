from omlish import check
from omlish import dataclasses as dc

from ...services import Response
from ..generations import ChatGeneration
from ..services import ChatRequest
from ..services import ChatServiceOutputs
from ..services import static_check_is_chat_service
from .services import ChatChoicesService


##


@static_check_is_chat_service
@dc.dataclass(frozen=True)
class ChatChoicesServiceChatService:
    service: ChatChoicesService

    async def invoke(self, request: ChatRequest) -> Response[ChatGeneration, ChatServiceOutputs]:
        resp = await self.service.invoke(request)
        return Response(check.single(resp.v.gs))  # , resp.outputs) FIXME: lol
