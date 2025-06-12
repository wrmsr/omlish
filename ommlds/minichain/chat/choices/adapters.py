from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...services import Response
from ..messages import AiMessage
from ..services import ChatRequest
from ..services import ChatService
from .services import ChatChoicesOutputs
from .services import ChatChoicesService


##


@dc.dataclass(frozen=True)
class ChatChoicesServiceChatService:
    service: ChatChoicesService

    def invoke(self, request: ChatRequest) -> Response[AiMessage, ChatChoicesOutputs]:
        resp = self.service.invoke(request)
        return Response(check.single(resp.v).m, resp.outputs)


lang.static_check_issubclass[ChatService](ChatChoicesServiceChatService)
