import typing as ta

from omlish import check
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from ....chat.choices.services import ChatChoicesOutputs
from ....chat.stream.services import ChatChoicesStreamRequest
from ....chat.stream.services import ChatChoicesStreamResponse
from ....chat.stream.services import static_check_is_chat_choices_stream_service
from ....chat.stream.types import AiChoiceDelta
from ....chat.stream.types import AiChoiceDeltas
from ....chat.stream.types import ChatChoicesStreamOption
from ....configs import Config
from ....resources import ResourcesOption
from ....resources import UseResources
from ....standard import ApiKey
from ....stream.services import StreamOption
from ....stream.services import new_stream_response
from .chat import OpenaiChatChoicesService
from .format import OpenaiChatRequestHandler
from .names import MODEL_NAMES


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='openai',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class OpenaiChatChoicesStreamService:
    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(OpenaiChatChoicesService.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env='OPENAI_API_KEY')

    READ_CHUNK_SIZE = 64 * 1024

    def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        # check.isinstance(request, ChatRequest)

        rh = OpenaiChatRequestHandler(
            request.v,
            *[
                o
                for o in request.options
                if not isinstance(o, (ChatChoicesStreamOption, StreamOption, ResourcesOption))
            ],
            model=MODEL_NAMES.resolve(self._model_name.v),
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

        with UseResources.or_new(request.options) as rs:
            http_client = rs.enter_context(http.client())
            http_response = rs.enter_context(http_client.stream_request(http_request))

            def yield_choices() -> ta.Generator[AiChoiceDeltas, None, ta.Sequence[ChatChoicesOutputs] | None]:
                db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
                sd = sse.SseDecoder()
                while True:
                    # FIXME: read1 not on response stream protocol
                    b = http_response.stream.read1(self.READ_CHUNK_SIZE)  # type: ignore[attr-defined]
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

                                # FIXME: stop reason
                                if not sj['choices']:
                                    continue

                                yield [
                                    AiChoiceDelta(rh.build_ai_message_delta(choice['delta']))
                                    for choice in sj['choices']
                                ]

                    if not b:
                        return []

            # raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))
            # return rh.build_response(raw_response)

            return new_stream_response(rs, yield_choices())
