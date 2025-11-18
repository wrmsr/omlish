import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from .....backends.groq import protocol as pt
from ....chat.choices.services import ChatChoicesOutputs
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.choices.stream.services import ChatChoicesStreamResponse
from ....chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ....chat.choices.stream.types import AiChoicesDeltas
from ....chat.tools.types import Tool
from ....configs import Config
from ....resources import UseResources
from ....standard import ApiKey
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response
from .chat import GroqChatChoicesService
from .names import MODEL_NAMES
from .protocol import build_gq_request_messages
from .protocol import build_gq_request_tool
from .protocol import build_mc_ai_choice_deltas


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='groq',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class GroqChatChoicesStreamService:
    def __init__(
            self,
            *configs: Config,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(GroqChatChoicesService.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env='GROQ_API_KEY')

    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        tools: list[pt.ChatCompletionRequest.Tool] = []
        with tv.TypedValues(*request.options).consume() as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(build_gq_request_tool(t))

        gq_request = pt.ChatCompletionRequest(
            messages=build_gq_request_messages(request.v),
            model=MODEL_NAMES.resolve(self._model_name.v),
            tools=tools or None,
            stream=True,
        )

        raw_request = msh.marshal(gq_request)

        http_request = http.HttpRequest(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        async with UseResources.or_new(request.options) as rs:
            http_client = await rs.enter_async_context(http.manage_async_client(self._http_client))
            http_response = await rs.enter_async_context(await http_client.stream_request(http_request))

            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs]:
                db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
                sd = sse.SseDecoder()
                while True:
                    b = await http_response.stream.read1(self.READ_CHUNK_SIZE)
                    for l in db.feed(b):
                        if isinstance(l, DelimitingBuffer.Incomplete):
                            # FIXME: handle
                            return []

                        # FIXME: https://platform.openai.com/docs/guides/function-calling?api-mode=responses#streaming
                        for so in sd.process_line(l):
                            if isinstance(so, sse.SseEvent) and so.type == b'message':
                                ss = so.data.decode('utf-8')
                                if ss == '[DONE]':
                                    return []

                                sj = json.loads(ss)  # ChatCompletionChunk

                                check.state(sj['object'] == 'chat.completion.chunk')

                                ccc = msh.unmarshal(sj, pt.ChatCompletionChunk)

                                # FIXME: stop reason
                                if not ccc.choices:
                                    continue

                                if any(choice.finish_reason for choice in ccc.choices):
                                    check.state(all(choice.finish_reason for choice in ccc.choices))
                                    break

                                await sink.emit(AiChoicesDeltas([
                                    build_mc_ai_choice_deltas(choice.delta)
                                    for choice in ccc.choices
                                ]))

                    if not b:
                        return []

            # raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))
            # return rh.build_response(raw_response)

            return await new_stream_response(rs, inner)
