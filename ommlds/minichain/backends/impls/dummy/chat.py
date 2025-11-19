# ruff: noqa: PERF402
import typing as ta

from omlish.text.lorem import LOREM

from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.choices.stream.services import ChatChoicesStreamResponse
from ....chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ....chat.choices.stream.types import AiChoiceDeltas
from ....chat.choices.stream.types import AiChoicesDeltas
from ....chat.choices.types import AiChoice
from ....chat.choices.types import ChatChoicesOutputs
from ....chat.messages import AiMessage
from ....chat.stream.types import ContentAiDelta
from ....resources import UseResources
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='dummy',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class DummyChatChoicesService:
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        return ChatChoicesResponse([AiChoice([AiMessage(LOREM)])])


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='dummy',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class DummyChatChoicesStreamService:
    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        async with UseResources.or_new(request.options) as rs:
            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs]:
                for s in LOREM:
                    await sink.emit(AiChoicesDeltas([
                        AiChoiceDeltas([
                            ContentAiDelta(s),
                        ]),
                    ]))

                return []

            return await new_stream_response(rs, inner)


##


# @omlish-manifest $.minichain.backends.strings.manifests.BackendStringsManifest(
#     [
#         'ChatChoicesService',
#         'ChatChoicesStreamService',
#     ],
#     'dummy',
# )
