"""
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
"""
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from .....backends.google.protocol import types as pt
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.choices.stream.services import ChatChoicesStreamResponse
from ....chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ....chat.choices.stream.types import AiChoiceDeltas
from ....chat.choices.stream.types import AiChoicesDeltas
from ....chat.choices.types import ChatChoicesOutputs
from ....chat.stream.types import ContentAiDelta
from ....chat.stream.types import ToolUseAiDelta
from ....chat.tools.types import Tool
from ....models.configs import ModelName
from ....resources import UseResources
from ....standard import ApiKey
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response
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
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env='GEMINI_API_KEY')

    BASE_URL: ta.ClassVar[str] = 'https://generativelanguage.googleapis.com/v1beta/models'

    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def invoke(
            self,
            request: ChatChoicesStreamRequest,
    ) -> ChatChoicesStreamResponse:
        key = check.not_none(self._api_key).reveal()

        g_tools: list[pt.Tool] = []
        with tv.TypedValues(*request.options).consume() as oc:
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

        model_name = MODEL_NAMES.resolve(self._model_name.v)

        http_request = http.HttpRequest(
            f'{self.BASE_URL.rstrip("/")}/{model_name}:streamGenerateContent?alt=sse&key={key}',
            headers={'Content-Type': 'application/json'},
            data=json.dumps_compact(req_dct).encode('utf-8'),
            method='POST',
        )

        async with UseResources.or_new(request.options) as rs:
            http_client = await rs.enter_async_context(http.manage_async_client(self._http_client))
            http_response = await rs.enter_async_context(await http_client.stream_request(http_request))

            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs] | None:
                db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
                sd = sse.SseDecoder()
                while True:
                    b = await http_response.stream.read1(self.READ_CHUNK_SIZE)
                    for l in db.feed(b):
                        if isinstance(l, DelimitingBuffer.Incomplete):
                            # FIXME: handle
                            raise TypeError(l)

                        for so in sd.process_line(l):
                            if isinstance(so, sse.SseEvent) and so.type == b'message':
                                gcr = msh.unmarshal(json.loads(so.data.decode('utf-8')), pt.GenerateContentResponse)  # noqa
                                cnd = check.single(check.not_none(gcr.candidates))

                                for p in check.not_none(cnd.content).parts or []:
                                    if (txt := p.text) is not None:
                                        check.none(p.function_call)
                                        await sink.emit(AiChoicesDeltas([
                                            AiChoiceDeltas([
                                                ContentAiDelta(check.not_none(txt)),
                                            ]),
                                        ]))

                                    elif (fc := p.function_call) is not None:
                                        check.none(p.text)
                                        await sink.emit(AiChoicesDeltas([
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

                    if not b:
                        return []

            return await new_stream_response(rs, inner)
