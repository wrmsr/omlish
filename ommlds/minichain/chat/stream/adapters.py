from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...services import Response
from ...tools.types import ToolUse
from ..choices.services import ChatChoicesRequest
from ..choices.services import static_check_is_chat_choices_service
from ..choices.types import AiChoice
from ..choices.types import AiChoices
from ..messages import AiMessage
from ..messages import AnyAiMessage
from ..messages import ToolUseMessage
from .services import ChatChoicesOutputs
from .services import ChatChoicesStreamOutputs
from .services import ChatChoicesStreamService
from .types import AiChoiceDelta
from .types import ContentAiChoiceDelta
from .types import ToolUseAiChoiceDelta


##


@static_check_is_chat_choices_service
@dc.dataclass(frozen=True)
class ChatChoicesStreamServiceChatChoicesService:
    service: ChatChoicesStreamService

    async def invoke(self, request: ChatChoicesRequest) -> Response[
        AiChoices,
        ChatChoicesOutputs | ChatChoicesStreamOutputs,
    ]:
        choice_lsts: list[list[list[str] | ToolUse]] = []

        def add(l: list[list[str] | ToolUse], d: AiChoiceDelta) -> None:
            if isinstance(d, ContentAiChoiceDelta):
                s = check.isinstance(d.c, str)
                if l and isinstance(l[-1], list):
                    l[-1].append(s)
                else:
                    l.append([s])

            elif isinstance(d, ToolUseAiChoiceDelta):
                l.append(d.tu)

            else:
                raise TypeError(d)

        async with (resp := await self.service.invoke(request)).v as it:  # noqa
            i = -1  # noqa
            l: list[list[str] | ToolUse]
            async for i, cs in lang.async_enumerate(it):
                if i == 0:
                    for c in cs.choices:
                        choice_lsts.append(l := [])
                        for d in c.deltas:
                            add(l, d)

                else:
                    for l, c in zip(choice_lsts, cs.choices, strict=True):
                        for d in c.deltas:
                            add(l, d)

        # check.state(resp_v.is_done)

        ret: list[AiChoice] = []
        for cl in choice_lsts:
            cc: list[AnyAiMessage] = []
            for e in cl:
                if isinstance(e, list):
                    cc.append(AiMessage(''.join(e)))
                elif isinstance(e, ToolUse):
                    cc.append(ToolUseMessage(e))
                else:
                    raise TypeError(e)
            ret.append(AiChoice(cc))

        # FIXME: outputs lol
        return Response(ret)
