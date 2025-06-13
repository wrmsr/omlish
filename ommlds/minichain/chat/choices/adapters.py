from omlish import check
from omlish import dataclasses as dc

from ...services import Response
from ..messages import AiMessage
from ..services import ChatRequest
from ..services import static_check_is_chat_service
from .services import ChatChoicesService
from .types import ChatChoicesOutputs


##


@static_check_is_chat_service
@dc.dataclass(frozen=True)
class ChatChoicesServiceChatService:
    service: ChatChoicesService

    def invoke(self, request: ChatRequest) -> Response[AiMessage, ChatChoicesOutputs]:
        resp = self.service.invoke(request)
        return Response(check.single(resp.v).m, resp.outputs)
