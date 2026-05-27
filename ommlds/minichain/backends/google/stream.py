"""https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models"""
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats.json import all as json
from omlish.http import all as http
from omlish.http import sse

from ....backends.google.protocol import types as pt
from ...chat.choices.stream.services import ChatChoicesStreamRequest
from ...chat.choices.stream.services import ChatChoicesStreamResponse
from ...chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ...chat.choices.stream.types import AiChoiceDeltas
from ...chat.choices.stream.types import AiChoicesDeltas
from ...chat.stream.types import ContentAiDelta
from ...chat.stream.types import ToolUseAiDelta
from ...chat.tools.types import Tool
from ...events.types import EventCallback
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceStreamResponseDataEvent
from ...http.stream import BytesHttpStreamResponseBuilder
from ...http.stream import SimpleSseLinesHttpStreamResponseHandler
from ...models.configs import ModelName
from ...standard import ApiKey
from .names import MODEL_NAMES
from .protocol import make_msg_content
from .protocol import pop_system_instructions
from .tools import build_tool_spec_schema


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='google',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class GoogleChatChoicesStreamService:
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(MODEL_NAMES.default))

    def __init__(
            self,
            *configs: ApiKey | ModelName,
            http_client: http.AsyncHttpClient | None = None,
            on_event: EventCallback | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client
        self._on_event = on_event

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env='GEMINI_API_KEY')

    BASE_URL: ta.ClassVar[str] = 'https://generativelanguage.googleapis.com/v1beta/models'

    async def _process_sse(self, so: sse.SseDecoderOutput) -> ta.Sequence[AiChoicesDeltas | None]:
        if not (isinstance(so, sse.SseEvent) and so.type == b'message'):
            return []

        sj = json.loads(so.data.decode('utf-8'))

        if self._on_event is not None:
            await self._on_event(ExternalServiceStreamResponseDataEvent(
                service=self,
                data=sj,
            ))

        gcr = msh.unmarshal(sj, pt.GenerateContentResponse)  # noqa
        cnd = check.single(check.not_none(gcr.candidates))

        out: list[AiChoicesDeltas | None] = []

        for p in check.not_none(cnd.content).parts or []:
            if (txt := p.text) is not None:
                check.none(p.function_call)
                out.append(AiChoicesDeltas([
                    AiChoiceDeltas([
                        ContentAiDelta(check.not_none(txt)),
                    ]),
                ]))

            elif (fc := p.function_call) is not None:
                check.none(p.text)
                out.append(AiChoicesDeltas([
                    AiChoiceDeltas([
                        ToolUseAiDelta(
                            id=fc.id,
                            name=fc.name,
                            args=fc.args,
                        ),
                    ]),
                ]))

            else:
                raise ValueError(p)

        return out

    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def invoke(
            self,
            request: ChatChoicesStreamRequest,
    ) -> ChatChoicesStreamResponse:
        key = check.not_none(self._api_key).reveal()

        g_tools: list[pt.Tool] = []
        with tv.consume(*request.options) as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                g_tools.append(pt.Tool(
                    function_declarations=[build_tool_spec_schema(t.spec)],
                ))

        msgs = list(request.v)

        system_inst = pop_system_instructions(msgs)

        g_req = pt.GenerateContentRequest(
            contents=[
                make_msg_content(m)
                for m in msgs
            ] or None,
            tools=g_tools or None,
            system_instruction=system_inst,
        )

        req_dct = msh.marshal(g_req)

        if self._on_event is not None:
            await self._on_event(ExternalServiceRequestEvent(
                service=self,
                request=req_dct,
            ))

        model_name = MODEL_NAMES.resolve(self._model_name.v)

        http_request = http.HttpClientRequest(
            f'{self.BASE_URL.rstrip("/")}/{model_name}:streamGenerateContent?alt=sse&key={key}',
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
