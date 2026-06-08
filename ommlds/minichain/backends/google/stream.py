"""https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models"""
import typing as ta

from omlish import marshal as msh
from omlish.formats.json import all as json
from omlish.http import all as http
from omlish.http import sse

from ....backends.google.protocol import types as pt
from ...chat.choices.stream.services import ChatChoicesStreamRequest
from ...chat.choices.stream.services import ChatChoicesStreamResponse
from ...chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ...chat.choices.stream.types import AiChoicesDeltas
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceStreamResponseDataEvent
from ...http.stream import BytesHttpStreamResponseBuilder
from ...http.stream import SimpleSseLinesHttpStreamResponseHandler
from .chat import BaseGoogleChatChoicesService
from .protocol import build_mc_ai_choices_deltas


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='google',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class GoogleChatChoicesStreamService(BaseGoogleChatChoicesService):
    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def _process_sse(self, so: sse.SseDecoderOutput) -> ta.Sequence[AiChoicesDeltas | None]:
        if not (isinstance(so, sse.SseEvent) and so.type == b'message'):
            return []

        sj = json.loads(so.data.decode('utf-8'))

        if self._on_event is not None:
            await self._on_event(ExternalServiceStreamResponseDataEvent(
                service=self,
                data=sj,
            ))

        return list(build_mc_ai_choices_deltas(msh.unmarshal(sj, pt.GenerateContentResponse)))

    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        g_req = self._build_request(request)

        req_dct = msh.marshal(g_req)

        if self._on_event is not None:
            await self._on_event(ExternalServiceRequestEvent(
                service=self,
                request=req_dct,
            ))

        http_request = http.HttpClientRequest(
            self._build_url('streamGenerateContent', query='alt=sse'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps_compact(req_dct).encode('utf-8'),
            method='POST',
        )

        return await BytesHttpStreamResponseBuilder(
            self._http_client,
            lambda http_response: SimpleSseLinesHttpStreamResponseHandler(self._process_sse).as_lines().as_bytes(),
            read_chunk_size=self.READ_CHUNK_SIZE,
            on_event=self._on_event,
        ).new_stream_response(
            http_request,
            request.options,
        )
