import typing as ta

from omlish import check
from omlish.formats import json
from omlish.http import all as http
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from ...chat.choices.services import ChatChoicesOutputs
from ...chat.choices.types import AiChoice
from ...chat.choices.types import AiChoices
from ...chat.stream.services import ChatChoicesStreamRequest
from ...chat.stream.services import ChatChoicesStreamResponse
from ...chat.stream.services import static_check_is_chat_choices_stream_service
from ...chat.stream.types import ChatChoicesStreamOption
from ...configs import Config
from ...configs import consume_configs
from ...resources import Resources
from ...standard import ApiKey
from ...standard import ModelName
from ...stream import ResponseGenerator
from .chat import OpenaiChatChoicesService
from .format import OpenaiChatRequestHandler


##


# @omlish-manifest $.minichain.registry.RegistryManifest(name='openai', type='ChatChoicesStreamService')
@static_check_is_chat_choices_stream_service
class OpenaiChatChoicesStreamService:
    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
            self._model_name = cc.pop(ModelName(OpenaiChatChoicesService.DEFAULT_MODEL_NAME))
            self._api_key = ApiKey.pop_secret(cc, env='OPENAI_API_KEY')

    READ_CHUNK_SIZE = 64 * 1024

    def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        # check.isinstance(request, ChatRequest)

        rh = OpenaiChatRequestHandler(
            request.v,
            *[o for o in request.options if not isinstance(o, ChatChoicesStreamOption)],
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

            def yield_choices() -> ta.Generator[AiChoices, None, ta.Sequence[ChatChoicesOutputs] | None]:
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

                                # FIXME: stop reason
                                if not sj['choices']:
                                    continue

                                yield [
                                    AiChoice(rh.build_ai_message(choice['delta']))
                                    for choice in sj['choices']
                                ]

                    if not b:
                        return []

            # raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))
            # return rh.build_response(raw_response)

            return ChatChoicesStreamResponse(rs.new_managed(ResponseGenerator(yield_choices())))
