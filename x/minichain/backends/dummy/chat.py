# ruff: noqa: PERF402
import typing as ta

from omlish import check
from omlish import typedvalues as tv
from omlish.text.lorem import LOREM

from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.types import ChatChoices
from ...chat.generations import ChatGeneration
from ...chat.messages import AiMessage
from ...chat.stream.choices.joining import AiChoicesDeltaJoiner
from ...chat.stream.choices.services import ChatChoicesStreamRequest
from ...chat.stream.choices.services import ChatChoicesStreamResponse
from ...chat.stream.choices.services import static_check_is_chat_choices_stream_service
from ...chat.stream.choices.types import AiChoiceDeltas
from ...chat.stream.choices.types import AiChoicesDeltas
from ...chat.stream.choices.types import ChatChoicesStreamResult
from ...chat.stream.types import ContentAiDelta
from ...configs import Config
from ...resources import UseResources
from ...services import StreamResponseSink
from ...services import new_stream_response


##


class DummyChatChoicesResponse(tv.UniqueScalarTypedValue[ChatChoices], Config):
    pass


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='dummy',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class DummyChatChoicesService:
    def __init__(
            self,
            *configs: DummyChatChoicesResponse,
    ) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            resp = cc.pop(DummyChatChoicesResponse, None)

        if resp is not None:
            self._resp = resp.v
        else:
            self._resp = self.make_string_response_choices([LOREM])

    @classmethod
    def make_string_response_choices(cls, strs: ta.Sequence[str]) -> ChatChoices:
        return ChatChoices([ChatGeneration([AiMessage(s)]) for s in check.not_isinstance(strs, str)])

    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        return ChatChoicesResponse(self._resp)


##


class DummyChatChoicesStreamResponse(tv.UniqueScalarTypedValue[ta.Sequence[AiChoicesDeltas]], Config):
    pass


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='dummy',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class DummyChatChoicesStreamService:
    def __init__(
            self,
            *configs: DummyChatChoicesStreamResponse,
    ) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            resp = cc.pop(DummyChatChoicesStreamResponse, None)

        if resp is not None:
            self._resp = resp.v
        else:
            self._resp = self.make_string_response_choices_deltas(list(LOREM))

    @classmethod
    def make_string_response_choices_deltas(cls, strs: ta.Sequence[str]) -> ta.Sequence[AiChoicesDeltas]:
        return [
            AiChoicesDeltas([
                AiChoiceDeltas([
                    ContentAiDelta(s),
                ]),
            ])
            for s in check.not_isinstance(strs, str)
        ]

    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        async with UseResources.or_new(request.options) as rs:
            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ChatChoicesStreamResult:
                joiner = AiChoicesDeltaJoiner()

                for x in self._resp:
                    joiner.add(x.choices)

                    await sink.emit(x)

                return ChatChoicesStreamResult(
                    ChatChoices([
                        ChatGeneration(jc)
                        for jc in joiner.build()
                    ]),
                )

            return await new_stream_response(rs, inner)


##


# @om-manifest $.minichain.specs.manifests.BackendStringsManifest(
#     [
#         'ChatChoicesService',
#         'ChatChoicesStreamService',
#     ],
#     'dummy',
# )
