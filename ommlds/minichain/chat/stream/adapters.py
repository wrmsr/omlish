import typing as ta

from omlish import dataclasses as dc

from ...services import Response
from ..messages import AiMessage
from ..services import ChatRequest
from .services import ChatChoicesResponseOutputs
from .services import ChatChoicesStreamService
from ..messages import ToolExecRequest


##


@dc.dataclass(frozen=True)
class ChatChoicesStreamServiceChatChoicesService:
    service: ChatChoicesStreamService

    class _Choice(ta.NamedTuple):
        s: list[str]
        trs: list[ToolExecRequest] = []

    def invoke(self, request: ChatRequest) -> Response[AiMessage, ChatChoicesResponseOutputs]:
        lst: list[ChatChoicesStreamServiceChatChoicesService._Choice] = []

        resp = self.service.invoke(request)
        with resp.v as resp_v:
            i = -1
            for i, cs in enumerate(resp_v):
                if i == 0:
                    raise NotImplementedError

        raise NotImplementedError
