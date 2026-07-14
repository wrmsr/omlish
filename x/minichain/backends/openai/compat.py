# ruff: noqa: SLF001
"""
The openai-compat chat-completions dialect service core. OpenAI's chat-completions wire format is a de-facto dialect
spoken by many vendors (groq, cerebras, ollama's openai endpoint, vllm, llama.cpp's server, ...); this module is the
*one* implementation of the dialect's service machinery - config consumption, request assembly (full option
handling), auth/headers, external-service event emission, the SSE envelope (`chat.completion.chunk` / `[DONE]` /
finish reasons) - parameterized by the handful of knobs that legitimately differ per vendor.

A compatible vendor backend is a ~20-line pair of subclasses setting `URL` / `API_KEY_ENV` / `EXTRA_HEADERS` /
`MODEL_NAMES` / `DEFAULT_MODEL_NAME` (see the groq and cerebras packages). Wire-level dialect extensions live as
marked optional fields on the reference protocol dataclasses (`ommlds/backends/openai/protocol`); translation-level
quirks live in this package's `protocol.py`. Genuinely different APIs (anthropic, google, ollama-native) are not
this dialect and do not belong here.
"""
import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh
from omcore import typedvalues as tv
from omcore.formats.json import all as json
from omcore.http import all as http
from omcore.http import sse

from ....backends.openai import protocol as pt
from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.types import ChatChoices
from ...chat.generations import ChatGeneration
from ...chat.stream.choices.joining import AiChoicesDeltaJoiner
from ...chat.stream.choices.services import ChatChoicesStreamRequest
from ...chat.stream.choices.services import ChatChoicesStreamResponse
from ...chat.stream.choices.types import AiChoiceDeltas
from ...chat.stream.choices.types import AiChoicesDeltas
from ...chat.stream.choices.types import ChatChoicesStreamOption
from ...chat.stream.choices.types import ChatChoicesStreamResult
from ...chat.stream.transform.types import AiDeltasTransform
from ...chat.stream.transform.types import AiDeltaTransformAiDeltasTransform
from ...chat.stream.transform.uuids import TypeSequentialMessageUuidAddingAiDeltaTransform
from ...events.types import EventCallback
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceResponseEvent
from ...external import ExternalServiceStreamResponseDataEvent
from ...http.stream import BytesHttpStreamResponseBuilder
from ...http.stream import HttpStreamResponseError
from ...http.stream import SseHttpStreamResponseHandler
from ...models.configs import ModelName
from ...models.names import ModelNameCollection
from ...resources import ResourcesOption
from ...services import StreamOption
from ...standard import ApiKey
from .names import CHAT_MODEL_NAMES
from .protocol import OpenaiChatRequestHandler
from .protocol import build_mc_ai_deltas
from .protocol import build_mc_choices_response
from .protocol import build_mc_stop_reason_output_
from .protocol import build_mc_token_usage_output_


##


class OpenaiCompatChatChoicesServiceBase(lang.Abstract):
    """Per-vendor knobs and shared config consumption for openai-compat chat-completions services."""

    URL: ta.ClassVar[str] = 'https://api.openai.com/v1/chat/completions'
    API_KEY_ENV: ta.ClassVar[str | None] = 'OPENAI_API_KEY'
    EXTRA_HEADERS: ta.ClassVar[ta.Mapping[ta.Any, ta.Any]] = {}

    MODEL_NAMES: ta.ClassVar[ModelNameCollection] = CHAT_MODEL_NAMES
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(CHAT_MODEL_NAMES.default))

    def __init__(
            self,
            # Deliberately the specific consumable union, not bare Config - spec resolution introspects it to
            # type-validate per-backend configs.
            *configs: ApiKey | ModelName,
            http_client: http.AsyncHttpClient | None = None,
            on_event: EventCallback | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client
        self._on_event = on_event

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env=self.API_KEY_ENV)

    #

    def _build_headers(self) -> dict[ta.Any, ta.Any]:
        return {
            http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
            http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(
                check.not_none(self._api_key).reveal(),
            ),
            **self.EXTRA_HEADERS,
        }

    def _build_request_handler(
            self,
            request: ChatChoicesRequest | ChatChoicesStreamRequest,
            *,
            stream: bool = False,
    ) -> OpenaiChatRequestHandler:
        return OpenaiChatRequestHandler(
            request.v,
            *[
                o
                for o in request.options
                if not isinstance(o, (ChatChoicesStreamOption, StreamOption, ResourcesOption))
            ],
            model=self.MODEL_NAMES.resolve(self._model_name.v),
            mandatory_kwargs=dict(
                stream=True,
                stream_options=pt.ChatCompletionRequest.StreamOptions(
                    include_usage=True,
                ),
            ) if stream else dict(
                stream=False,
            ),
        )


##


class OpenaiCompatChatChoicesService(OpenaiCompatChatChoicesServiceBase, lang.Abstract):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        rh = self._build_request_handler(request)

        raw_request = msh.marshal(rh.oai_request())

        if self._on_event is not None:
            await self._on_event(ExternalServiceRequestEvent(
                service=self,
                request=raw_request,
            ))

        http_response = await http.async_request(
            self.URL,
            headers=self._build_headers(),
            data=json.dumps(raw_request).encode('utf-8'),
            client=self._http_client,
        )

        if http_response.status != 200:
            raise HttpStreamResponseError(http_response, data=http_response.data)

        raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))

        if self._on_event is not None:
            await self._on_event(ExternalServiceResponseEvent(
                service=self,
                response=raw_response,
            ))

        return build_mc_choices_response(msh.unmarshal(raw_response, pt.ChatCompletionResponse))


##


class OpenaiCompatChatChoicesStreamService(OpenaiCompatChatChoicesServiceBase, lang.Abstract):
    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    class _ResponseHandler(SseHttpStreamResponseHandler):
        def __init__(self, o: OpenaiCompatChatChoicesStreamService) -> None:
            super().__init__()

            self._o = o

            self._joiner = AiChoicesDeltaJoiner()

            self._dts: list[AiDeltasTransform] | None = None

            self._finish_choices: dict[int, pt.ChatCompletionChunkChoice] = {}
            self._final_chunk: pt.ChatCompletionChunk | None = None

        async def process_sse(self, so: sse.SseDecoderOutput) -> ta.Sequence[AiChoicesDeltas | None]:
            if not (isinstance(so, sse.SseEvent) and so.type == b'message'):
                return []

            ss = so.data.decode('utf-8')
            if ss == '[DONE]':
                return [None]

            sj = json.loads(ss)  # ChatCompletionChunk

            if self._o._on_event is not None:
                await self._o._on_event(ExternalServiceStreamResponseDataEvent(
                    service=self,
                    data=sj,
                ))

            check.state(sj['object'] == 'chat.completion.chunk')

            ccc = msh.unmarshal(sj, pt.ChatCompletionChunk)

            if not ccc.choices:
                self._final_chunk = ccc
                return []

            for i, choice in enumerate(ccc.choices):
                if choice.finish_reason is not None:
                    self._finish_choices[i] = choice

            csds = AiChoicesDeltas([
                AiChoiceDeltas(build_mc_ai_deltas(choice.delta))
                for choice in ccc.choices
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

            return [csds]

        async def finish(self) -> ChatChoicesStreamResult:
            return ChatChoicesStreamResult(
                ChatChoices(
                    [
                        ChatGeneration(
                            jc,

                            tv.collect(
                                *(
                                    build_mc_stop_reason_output_(fch.finish_reason)
                                    if (fch := self._finish_choices.get(i)) is not None else []
                                ),
                            ),
                        )

                        for i, jc in enumerate(self._joiner.build())
                    ],

                    tv.collect(
                        *(
                            build_mc_token_usage_output_(fcc.usage)
                            if (fcc := self._final_chunk) is not None else []
                        ),
                    ),
                ),
            )

    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        rh = self._build_request_handler(request, stream=True)

        raw_request = msh.marshal(rh.oai_request())

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
