import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...services import Response
from ..choices.services import ChatChoicesRequest
from ..choices.services import ChatChoicesService
from ..choices.types import AiChoice
from ..choices.types import AiChoices
from ..messages import AiMessage
from ..messages import ToolExecRequest
from .services import ChatChoicesOutputs
from .services import ChatChoicesStreamOutputs
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
        ChatChoicesOutputs | ChatChoicesStreamOutputs,
    ]:
        lst: list[ChatChoicesStreamServiceChatChoicesService._Choice] = []

        resp = self.service.invoke(request)
        with resp.v as resp_v:
            i = -1  # noqa
            for i, cs in enumerate(resp_v):
                if i == 0:
                    for c in cs:
                        m = c.m
                        lst.append(self._Choice(
                            [m.s] if m.s is not None else [],
                            list(m.tool_exec_requests or []),
                        ))

                else:
                    for ch, c in zip(lst, cs, strict=True):
                        m = c.m
                        if m.s is not None:
                            ch.parts.append(m.s)
                        if m.tool_exec_requests:
                            ch.trs.extend(m.tool_exec_requests)

        check.state(resp_v.is_done)

        ret: list[AiChoice] = []
        for ch in lst:
            ret.append(AiChoice(AiMessage(
                ''.join(ch.parts) if ch.parts else None,
                ch.trs or None,
            )))

        # FIXME: outputs lol
        return Response(ret)


lang.static_check_issubclass[ChatChoicesService](ChatChoicesStreamServiceChatChoicesService)
