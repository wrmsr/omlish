from omlish import dataclasses as dc

from ...services import Response
from ..choices.services import ChatChoicesRequest
from ..choices.services import static_check_is_chat_choices_service
from ..choices.types import AiChoice
from ..choices.types import AiChoices
from .joining import AiChoiceDeltaJoiner
from .services import ChatChoicesOutputs
from .services import ChatChoicesStreamOutputs
from .services import ChatChoicesStreamService


##


@static_check_is_chat_choices_service
@dc.dataclass(frozen=True)
class ChatChoicesStreamServiceChatChoicesService:
    service: ChatChoicesStreamService

    async def invoke(self, request: ChatChoicesRequest) -> Response[
        AiChoices,
        ChatChoicesOutputs | ChatChoicesStreamOutputs,
    ]:
        joiner = AiChoiceDeltaJoiner()

        async with (resp := await self.service.invoke(request)).v as it:  # noqa
            async for cs in it:
                joiner.add(cs.choices)

        # check.state(resp_v.is_done)

        # FIXME: outputs lol
        return Response([AiChoice(ms) for ms in joiner.build()])
