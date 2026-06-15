import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish.formats.json import all as json
from omlish.http import all as http
from omlish.http import sse

from ....backends.anthropic.protocol.sse.events import AnthropicSseDecoderEvents
from ...chat.stream.choices.services import ChatChoicesStreamRequest
from ...chat.stream.choices.services import ChatChoicesStreamResponse
from ...chat.stream.choices.services import static_check_is_chat_choices_stream_service
from ...chat.stream.choices.types import AiChoiceDeltas
from ...chat.stream.choices.types import AiChoicesDeltas
from ...chat.stream.choices.types import ChatChoicesStreamResult
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceStreamResponseDataEvent
from ...http.stream import BytesHttpStreamResponseBuilder
from ...http.stream import SseHttpStreamResponseHandler
from .chat import AnthropicChatChoicesServiceBase
from .protocol import AnthropicSseDeltaTranslator


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='anthropic',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class AnthropicChatChoicesStreamService(AnthropicChatChoicesServiceBase):
    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def _process_sse(
            self,
            translator: AnthropicSseDeltaTranslator,
            so: sse.SseDecoderOutput,
    ) -> ta.Sequence[AiChoicesDeltas | None]:
        if not isinstance(so, sse.SseEvent):
            return []

        dct = json.loads(so.data.decode('utf-8'))
        check.equal(dct['type'], so.type.decode('utf-8'))

        if self._on_event is not None:
            await self._on_event(ExternalServiceStreamResponseDataEvent(
                service=self,
                data=dct,
            ))

        ev = msh.unmarshal(dct, AnthropicSseDecoderEvents.Event)

        res = translator.translate(ev)

        out: list[AiChoicesDeltas | None] = []
        if res.deltas:
            out.append(AiChoicesDeltas([AiChoiceDeltas(res.deltas)]))
        if res.done:
            out.append(None)
        return out

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

        translator = AnthropicSseDeltaTranslator()

        return await BytesHttpStreamResponseBuilder(
            self._http_client,
            lambda http_response: _AnthropicSseHandler(self, translator).as_lines().as_bytes(),
            read_chunk_size=self.READ_CHUNK_SIZE,
            on_event=self._on_event,
        ).new_stream_response(
            http_request,
            request.options,
        )


class _AnthropicSseHandler(SseHttpStreamResponseHandler):
    """Bridges the shared sse builder to the service's `_process_sse`, validating end-state at stream close."""

    def __init__(
            self,
            service: AnthropicChatChoicesStreamService,
            translator: AnthropicSseDeltaTranslator,
    ) -> None:
        super().__init__()

        self._service = service
        self._translator = translator

    async def process_sse(self, so: sse.SseDecoderOutput) -> ta.Sequence[ta.Any]:
        return await self._service._process_sse(self._translator, so)  # noqa

    async def finish(self) -> ta.Any:
        self._translator.finish()
        return ChatChoicesStreamResult()  # FIXME: outputs lol
