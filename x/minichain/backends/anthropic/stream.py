# ruff: noqa: SLF001
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish.formats.json import all as json
from omlish.http import all as http
from omlish.http import sse

from ....backends.anthropic.protocol.sse.events import AnthropicSseDecoderEvents
from ...chat.choices.types import ChatChoices
from ...chat.generations import ChatGeneration
from ...chat.stream.choices.joining import AiChoicesDeltaJoiner
from ...chat.stream.choices.services import ChatChoicesStreamRequest
from ...chat.stream.choices.services import ChatChoicesStreamResponse
from ...chat.stream.choices.services import static_check_is_chat_choices_stream_service
from ...chat.stream.choices.types import AiChoiceDeltas
from ...chat.stream.choices.types import AiChoicesDeltas
from ...chat.stream.choices.types import ChatChoicesStreamResult
from ...chat.stream.transform.types import AiDeltasTransform
from ...chat.stream.transform.types import AiDeltaTransformAiDeltasTransform
from ...chat.stream.transform.uuids import TypeSequentialMessageUuidAddingAiDeltaTransform
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceStreamResponseDataEvent
from ...http.stream import BytesHttpStreamResponseBuilder
from ...http.stream import SseHttpStreamResponseHandler
from .chat import AnthropicChatChoicesServiceBase
from .protocol import AnthropicSseDeltaTranslator


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='anthropic',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class AnthropicChatChoicesStreamService(AnthropicChatChoicesServiceBase):
    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    class _ResponseHandler(SseHttpStreamResponseHandler):
        """Bridges the shared sse builder to the service's `_process_sse`, validating end-state at stream close."""

        def __init__(self, o: AnthropicChatChoicesStreamService) -> None:
            super().__init__()

            self._o = o

            self._translator = AnthropicSseDeltaTranslator()
            self._joiner = AiChoicesDeltaJoiner()
            self._dts: list[AiDeltasTransform] | None = None

        async def process_sse(self, so: sse.SseDecoderOutput) -> ta.Sequence[AiChoicesDeltas | None]:
            if not isinstance(so, sse.SseEvent):
                return []

            dct = json.loads(so.data.decode('utf-8'))
            check.equal(dct['type'], so.type.decode('utf-8'))

            if self._o._on_event is not None:
                await self._o._on_event(ExternalServiceStreamResponseDataEvent(
                    service=self,
                    data=dct,
                ))

            ev = msh.unmarshal(dct, AnthropicSseDecoderEvents.Event)

            res = self._translator.translate(ev)

            out: list[AiChoicesDeltas | None] = []

            if res.deltas:
                csds = AiChoicesDeltas([
                    AiChoiceDeltas(res.deltas),
                ])

                if (dts := self._dts) is None:
                    dts = self._dts = [
                        # FIXME: YES THIS IS GETTING WORSE TO GET BETTER
                        AiDeltaTransformAiDeltasTransform(
                            TypeSequentialMessageUuidAddingAiDeltaTransform(),
                        )
                        for _ in range(len(csds.choices))
                    ]

                csds = dc.replace(csds, choices=[
                    dc.replace(cds, deltas=dts[i].transform(cds.deltas))
                    for i, cds in enumerate(csds.choices)
                ])

                self._joiner.add(csds.choices)

                out.append(csds)

            if res.done:
                out.append(None)

            return out

        async def finish(self) -> ta.Any:
            self._translator.finish()

            return ChatChoicesStreamResult(
                ChatChoices([
                    ChatGeneration(jc)
                    for jc in self._joiner.build()
                ]),
            )

    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        a_req = self._build_request(request, stream=True)

        raw_request = msh.marshal(a_req)

        if self._on_event is not None:
            await self._on_event(ExternalServiceRequestEvent(
                service=self,
                request=raw_request,
            ))

        http_request = http.HttpClientRequest(
            self.URL,
            headers=self._build_headers(),
            data=json.dumps(raw_request).encode('utf-8'),
        )

        return await BytesHttpStreamResponseBuilder(
            self._http_client,
            lambda http_response: self._ResponseHandler(self).as_lines().as_bytes(),
            read_chunk_size=self.READ_CHUNK_SIZE,
            on_event=self._on_event,
        ).new_stream_response(
            http_request,
            request.options,
        )
