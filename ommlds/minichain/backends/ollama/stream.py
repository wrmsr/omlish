import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish.formats.json import all as json
from omlish.http import all as http

from ....backends.ollama import protocol as pt
from ...chat.choices.stream.services import ChatChoicesStreamRequest
from ...chat.choices.stream.services import ChatChoicesStreamResponse
from ...chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ...chat.choices.stream.types import AiChoicesDeltas
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceStreamResponseDataEvent
from ...http.stream import BytesHttpStreamResponseBuilder
from ...http.stream import SimpleLinesHttpStreamResponseHandler
from .chat import BaseOllamaChatChoicesService
from .protocol import build_mc_ai_choice_deltas


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='ollama',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class OllamaChatChoicesStreamService(BaseOllamaChatChoicesService):
    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def _process_line(self, line: lang.Bytes) -> ta.Sequence[AiChoicesDeltas]:
        # Ollama's native stream is JSONL: each line is a complete ChatResponse delta (the final one carries `done`
        # and stats with no content, translating to no deltas).
        lj = json.loads(bytes(line).decode('utf-8'))

        if self._on_event is not None:
            await self._on_event(ExternalServiceStreamResponseDataEvent(
                service=self,
                data=lj,
            ))

        lp = msh.unmarshal(lj, pt.ChatResponse)

        if (ds := build_mc_ai_choice_deltas(lp)).deltas:
            return [AiChoicesDeltas([ds])]
        return []

    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        a_req = self._build_request(request, stream=True)

        raw_request = msh.marshal(a_req)

        if self._on_event is not None:
            await self._on_event(ExternalServiceRequestEvent(
                service=self,
                request=raw_request,
            ))

        http_request = http.HttpClientRequest(
            self._chat_url(),
            data=json.dumps(raw_request).encode('utf-8'),
        )

        return await BytesHttpStreamResponseBuilder(
            self._http_client,
            lambda http_response: SimpleLinesHttpStreamResponseHandler(self._process_line).as_bytes(),
            read_chunk_size=self.READ_CHUNK_SIZE,
            on_event=self._on_event,
        ).new_stream_response(
            http_request,
            request.options,
        )
