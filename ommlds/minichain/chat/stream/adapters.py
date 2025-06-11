import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ...services import Response
from ..choices.services import ChatChoicesRequest
from ..choices.services import ChatChoicesService
from ..choices.types import AiChoices
from ..messages import ToolExecRequest
from .services import ChatChoicesResponseOutputs
from .services import ChatChoicesStreamResponseOutputs
from .services import ChatChoicesStreamService


##


@dc.dataclass(frozen=True)
class ChatChoicesStreamServiceChatChoicesService:
    service: ChatChoicesStreamService

    class _Choice(ta.NamedTuple):
        parts: list[str]
        trs: list[ToolExecRequest]

    def invoke(self, request: ChatChoicesRequest) -> Response[
        AiChoices,
        ChatChoicesResponseOutputs | ChatChoicesStreamResponseOutputs,
    ]:
        lst: list[ChatChoicesStreamServiceChatChoicesService._Choice] = []

        resp = self.service.invoke(request)
        with resp.v as resp_v:
            i = -1
            for i, cs in enumerate(resp_v):
                if i == 0:
                    for c in cs:
                        m = c.m
                        lst.append(self._Choice(
                            [m.s] if m.s is not None else [],
                            list(m.tool_exec_requests or []),
                        ))

                else:
                    for lc, c in zip(lst, cs, strict=True):
                        m = c.m
                        if m.s is not None:
                            lc.parts.append(m.s)
                        if m.tool_exec_requests:
                            lc.trs.extend(m.tool_exec_requests)

        raise NotImplementedError


lang.static_check_issubclass[ChatChoicesService](ChatChoicesStreamServiceChatChoicesService)
