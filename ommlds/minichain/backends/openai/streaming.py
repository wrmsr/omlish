import typing as ta

from omlish import check
from omlish.formats import json
from omlish.http import all as http
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from ...chat.choices import AiChoice
from ...chat.choices import AiChoices
from ...chat.messages import AiMessage
from ...chat.streaming import ChatStreamRequest
from ...chat.streaming import ChatStreamResponse
from ...chat.streaming import ChatStreamService_
from ...configs import Config
from ...configs import consume_configs
from ...resources import Resources
from ...standard import ApiKey
from ...standard import ModelName
from .chat import OpenaiChatService
from .format import OpenaiChatRequestHandler


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(name='openai', type='ChatStreamService')
class OpenaiChatStreamService(ChatStreamService_):
    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
            self._model_name = cc.pop(ModelName(OpenaiChatService.DEFAULT_MODEL_NAME))
            self._api_key = ApiKey.pop_secret(cc, env='OPENAI_API_KEY')

    READ_CHUNK_SIZE = 64 * 1024

    def invoke(self, request: ChatStreamRequest) -> ChatStreamResponse:
        check.isinstance(request, ChatStreamRequest)

        rh = OpenaiChatRequestHandler(
            request.chat,
            *request.options,
            model=self._model_name.v,
            mandatory_kwargs=dict(
                stream=True,
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

        rs = Resources()
        try:
            http_client = rs.enter_context(http.client())
            http_response = rs.enter_context(http_client.stream_request(http_request))

            def yield_choices() -> ta.Iterator[AiChoices]:
                db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
                sd = sse.SseDecoder()
                while True:
                    b = http_response.stream.read1(self.READ_CHUNK_SIZE)  # FIXME: read1 not on response stream protocol
                    for l in db.feed(b):
                        if isinstance(l, DelimitingBuffer.Incomplete):
                            # FIXME: handle
                            return

                        for so in sd.process_line(l):
                            if isinstance(so, sse.SseEvent) and so.type == b'message':
                                ss = so.data.decode('utf-8')
                                if ss == '[DONE]':
                                    return

                                sj = json.loads(ss)

                                check.state(sj['object'] == 'chat.completion.chunk')

                                yield [
                                    AiChoice(
                                        AiMessage(
                                            choice['delta'].get('content', ''),
                                        ),
                                    )
                                    for choice in sj['choices']
                                ]

                    if not b:
                        return

            # raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))
            # return rh.build_response(raw_response)

            return ChatStreamResponse(
                _iterator=yield_choices(),
                _resources=rs,
            )

        except Exception:
            rs.close()
            raise
