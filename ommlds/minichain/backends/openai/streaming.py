import typing as ta

from omlish import check
from omlish.formats import json
from omlish.http import all as http
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from ...chat.choices import AiChoice
from ...chat.choices import AiChoices
from ...chat.services import ChatRequest
from ...chat.services import ChatResponseOutputs
from ...chat.streaming import ChatStreamResponse
from ...chat.streaming import ChatStreamService
from ...configs import Config
from ...configs import consume_configs
from ...resources import Resources
from ...standard import ApiKey
from ...standard import ModelName
from ...streaming import ResponseGenerator
from .chat import OpenaiChatService
from .format import OpenaiChatRequestHandler


##


# @omlish-manifest ommlds.minichain.registry.RegistryManifest(name='openai', type='ChatStreamService')
class OpenaiChatStreamService(ChatStreamService):
    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
            self._model_name = cc.pop(ModelName(OpenaiChatService.DEFAULT_MODEL_NAME))
            self._api_key = ApiKey.pop_secret(cc, env='OPENAI_API_KEY')

    READ_CHUNK_SIZE = 64 * 1024

    def invoke(self, request: ChatRequest) -> ChatStreamResponse:
        # check.isinstance(request, ChatRequest)

        rh = OpenaiChatRequestHandler(
            request.v,
            *request.options,
            model=self._model_name.v,
            mandatory_kwargs=dict(
                stream=True,
                stream_options=dict(
                    include_usage=True,
                ),
            ),
        )

        raw_request = rh.raw_request()

        http_request = http.HttpRequest(
            'https://api.openai.com/v1/chat/completions',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        with Resources.new() as rs:
            http_client = rs.enter_context(http.client())
            http_response = rs.enter_context(http_client.stream_request(http_request))

            def yield_choices() -> ta.Generator[AiChoices, None, ta.Sequence[ChatResponseOutputs] | None]:
                db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
                sd = sse.SseDecoder()
                while True:
                    # FIXME: read1 not on response stream protocol
                    b = http_response.stream.read1(self.READ_CHUNK_SIZE)  # type: ignore[attr-defined]
                    for l in db.feed(b):
                        if isinstance(l, DelimitingBuffer.Incomplete):
                            # FIXME: handle
                            return []

                        for so in sd.process_line(l):
                            if isinstance(so, sse.SseEvent) and so.type == b'message':
                                ss = so.data.decode('utf-8')
                                if ss == '[DONE]':
                                    return []

                                sj = json.loads(ss)  # ChatCompletionChunk

                                check.state(sj['object'] == 'chat.completion.chunk')

                                yield [
                                    AiChoice(rh.build_ai_message(choice['delta']))
                                    for choice in sj['choices']
                                ]

                    if not b:
                        return []

            # raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))
            # return rh.build_response(raw_response)

            return ChatStreamResponse(rs.new_managed(ResponseGenerator(yield_choices())))
