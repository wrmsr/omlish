from omlish import check
from omlish import dataclasses as dc

from ...services import Response
from ..messages import AiMessage
from ..services import ChatRequest
from .services import ChatChoicesResponseOutputs
from .services import ChatChoicesService


##


@dc.dataclass(frozen=True)
class ChatChoicesServiceChatService:
    chat_choices_service: ChatChoicesService

    def invoke(self, request: ChatRequest) -> Response[AiMessage, ChatChoicesResponseOutputs]:
        resp = self.chat_choices_service.invoke(request)
        return Response(check.single(resp.v).m, resp.outputs)
