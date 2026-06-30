# ruff: noqa: SLF001
"""https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models"""
import typing as ta

from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish.formats.json import all as json
from omlish.http import all as http
from omlish.http import sse

from ....backends.google.protocol import types as pt
from ...chat.choices.types import ChatChoices
from ...chat.generations import ChatGeneration
from ...chat.stream.choices.joining import AiChoicesDeltaJoiner
from ...chat.stream.choices.services import ChatChoicesStreamRequest
from ...chat.stream.choices.services import ChatChoicesStreamResponse
from ...chat.stream.choices.services import static_check_is_chat_choices_stream_service
from ...chat.stream.choices.types import AiChoicesDeltas
from ...chat.stream.choices.types import ChatChoicesStreamResult
from ...chat.stream.transform.types import AiDeltasTransform
from ...chat.stream.transform.types import AiDeltaTransformAiDeltasTransform
from ...chat.stream.transform.uuids import TypeSequentialMessageUuidAddingAiDeltaTransform
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceStreamResponseDataEvent
from ...http.stream import BytesHttpStreamResponseBuilder
from ...http.stream import SseHttpStreamResponseHandler
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

    class _ResponseHandler(SseHttpStreamResponseHandler):
        def __init__(self, o: GoogleChatChoicesStreamService) -> None:
            super().__init__()

            self._o = o

            self._dts: list[AiDeltasTransform] | None = None
            self._joiner = AiChoicesDeltaJoiner()

        async def process_sse(self, so: sse.SseDecoderOutput) -> ta.Sequence[AiChoicesDeltas | None]:
            if not (isinstance(so, sse.SseEvent) and so.type == b'message'):
                return []

            sj = json.loads(so.data.decode('utf-8'))

            if self._o._on_event is not None:
                await self._o._on_event(ExternalServiceStreamResponseDataEvent(
                    service=self,
                    data=sj,
                ))

            built = list(build_mc_ai_choices_deltas(msh.unmarshal(sj, pt.GenerateContentResponse)))

            out: list[AiChoicesDeltas] = []

            for csds in built:
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

                out.append(csds)
                self._joiner.add(csds.choices)

            return out

        async def finish(self) -> ta.Any:
            return ChatChoicesStreamResult(
                ChatChoices([
                    ChatGeneration(jc)
                    for jc in self._joiner.build()
                ]),
            )

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
            lambda http_response: self._ResponseHandler(self).as_lines().as_bytes(),
            read_chunk_size=self.READ_CHUNK_SIZE,
            on_event=self._on_event,
        ).new_stream_response(
            http_request,
            request.options,
        )
