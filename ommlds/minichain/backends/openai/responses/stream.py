"""https://platform.openai.com/docs/api-reference/responses-streaming"""
import typing as ta

from omlish import marshal as msh
from omlish.formats.json import all as json
from omlish.http import all as http
from omlish.http import sse

from .....backends.openai.protocol import responses as pt
from ....chat.stream.choices.services import ChatChoicesStreamRequest
from ....chat.stream.choices.services import ChatChoicesStreamResponse
from ....chat.stream.choices.services import static_check_is_chat_choices_stream_service
from ....chat.stream.choices.types import AiChoiceDeltas
from ....chat.stream.choices.types import AiChoicesDeltas
from ....external import ExternalServiceRequestEvent
from ....external import ExternalServiceStreamResponseDataEvent
from ....http.stream import BytesHttpStreamResponseBuilder
from ....http.stream import SimpleSseLinesHttpStreamResponseHandler
from .chat import OpenaiResponsesServiceBase
from .protocol import ResponsesSseDeltaTranslator


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='openai-responses',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class OpenaiResponsesChatChoicesStreamService(OpenaiResponsesServiceBase):
    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def _process_sse(
            self,
            translator: ResponsesSseDeltaTranslator,
            so: sse.SseDecoderOutput,
    ) -> ta.Sequence[AiChoicesDeltas | None]:
        if not isinstance(so, sse.SseEvent):
            return []

        sj = json.loads(so.data.decode('utf-8'))

        if self._on_event is not None:
            await self._on_event(ExternalServiceStreamResponseDataEvent(
                service=self,
                data=sj,
            ))

        ev = msh.unmarshal(sj, pt.ResponsesSseEvents.Event)

        res = translator.translate(ev)

        out: list[AiChoicesDeltas | None] = []
        if res.deltas:
            out.append(AiChoicesDeltas([AiChoiceDeltas(res.deltas)]))
        if res.done:
            out.append(None)
        return out

    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        rsp_request = self._build_rsp_request(request, stream=True)

        raw_request = msh.marshal(rsp_request)

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

        translator = ResponsesSseDeltaTranslator()

        return await BytesHttpStreamResponseBuilder(
            self._http_client,
            lambda http_response: SimpleSseLinesHttpStreamResponseHandler(
                lambda so: self._process_sse(translator, so),
            ).as_lines().as_bytes(),
            read_chunk_size=self.READ_CHUNK_SIZE,
            on_event=self._on_event,
        ).new_stream_response(
            http_request,
            request.options,
        )
