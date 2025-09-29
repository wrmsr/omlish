import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...services import Response
from ..choices.services import ChatChoicesRequest
from ..choices.services import static_check_is_chat_choices_service
from ..choices.types import AiChoice
from ..choices.types import AiChoices
from ..messages import AiMessage
from ..messages import ToolUse
from .services import ChatChoicesOutputs
from .services import ChatChoicesStreamOutputs
from .services import ChatChoicesStreamService


##


@static_check_is_chat_choices_service
@dc.dataclass(frozen=True)
class ChatChoicesStreamServiceChatChoicesService:
    service: ChatChoicesStreamService

    class _Choice(ta.NamedTuple):
        parts: list[str]
        trs: list[ToolUse]

    async def invoke(self, request: ChatChoicesRequest) -> Response[
        AiChoices,
        ChatChoicesOutputs | ChatChoicesStreamOutputs,
    ]:
        lst: list[ChatChoicesStreamServiceChatChoicesService._Choice] = []

        async with (resp := await self.service.invoke(request)).v as it:  # noqa
            i = -1  # noqa
            async for i, cs in lang.async_enumerate(it):
                if i == 0:
                    for c in cs:
                        m = c.m
                        lst.append(self._Choice(
                            [check.isinstance(m.c, str)] if m.c is not None else [],
                            # FIXME
                            # list(m.tool_exec_requests or []),
                            [],
                        ))

                else:
                    for ch, c in zip(lst, cs, strict=True):
                        m = c.m
                        if m.c is not None:
                            ch.parts.append(check.isinstance(m.c, str))
                        # FIXME
                        # if m.tool_exec_requests:
                        #     ch.trs.extend(m.tool_exec_requests)

        # check.state(resp_v.is_done)

        ret: list[AiChoice] = []
        for ch in lst:
            ret.append(AiChoice(AiMessage(
                ''.join(ch.parts) if ch.parts else None,
                ch.trs or None,
            )))

        # FIXME: outputs lol
        return Response(ret)
