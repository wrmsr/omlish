# ruff: noqa: SLF001
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats.json import all as json
from omlish.http import all as http

from ....backends.ollama import protocol as pt
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
from ...http.stream import LinesHttpStreamResponseHandler
from .chat import BaseOllamaChatChoicesService
from .protocol import build_mc_ai_choice_deltas


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='ollama',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class OllamaChatChoicesStreamService(BaseOllamaChatChoicesService):
    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    class _ResponseHandler(LinesHttpStreamResponseHandler):
        # Ollama's native stream is JSONL: each line is a complete ChatResponse delta (the final one carries `done` and
        # stats with no content, translating to no deltas).

        def __init__(self, o: OllamaChatChoicesStreamService) -> None:
            super().__init__()

            self._o = o

            self._dts: list[AiDeltasTransform] | None = None
            self._joiner = AiChoicesDeltaJoiner()

        async def process_line(self, line: lang.Bytes) -> ta.Sequence[AiChoicesDeltas]:
            lj = json.loads(bytes(line).decode('utf-8'))

            if self._o._on_event is not None:
                await self._o._on_event(ExternalServiceStreamResponseDataEvent(
                    service=self,
                    data=lj,
                ))

            lp = msh.unmarshal(lj, pt.ChatResponse)

            if (ds := build_mc_ai_choice_deltas(lp)).deltas:
                csds = AiChoicesDeltas([ds])

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

                return [csds]

            return []

        async def finish(self) -> ta.Any:
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
            self._chat_url(),
            data=json.dumps(raw_request).encode('utf-8'),
        )

        return await BytesHttpStreamResponseBuilder(
            self._http_client,
            lambda http_response: self._ResponseHandler(self).as_bytes(),
            read_chunk_size=self.READ_CHUNK_SIZE,
            on_event=self._on_event,
        ).new_stream_response(
            http_request,
            request.options,
        )
