# ruff: noqa: PERF402
import typing as ta

from omlish import check
from omlish import typedvalues as tv
from omlish.text.lorem import LOREM

from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.stream.services import ChatChoicesStreamRequest
from ...chat.choices.stream.services import ChatChoicesStreamResponse
from ...chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ...chat.choices.stream.types import AiChoiceDeltas
from ...chat.choices.stream.types import AiChoicesDeltas
from ...chat.choices.types import ChatChoice
from ...chat.choices.types import ChatChoices
from ...chat.choices.types import ChatChoicesOutputs
from ...chat.messages import AiMessage
from ...chat.stream.types import ContentAiDelta
from ...configs import Config
from ...resources import UseResources
from ...services import StreamResponseSink
from ...services import new_stream_response


##


class DummyChatChoicesResponse(tv.UniqueScalarTypedValue[ChatChoices], Config):
    pass


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
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
        return [ChatChoice([AiMessage(s)]) for s in check.not_isinstance(strs, str)]

    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        return ChatChoicesResponse(self._resp)


##


class DummyChatChoicesStreamResponse(tv.UniqueScalarTypedValue[ta.Sequence[AiChoicesDeltas]], Config):
    pass


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
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
            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs]:
                for x in self._resp:
                    await sink.emit(x)

                return []

            return await new_stream_response(rs, inner)


##


# @omlish-manifest $.minichain.specs.manifests.BackendStringsManifest(
#     [
#         'ChatChoicesService',
#         'ChatChoicesStreamService',
#     ],
#     'dummy',
# )
