import typing as ta

from omlish import check
from omlish import lang
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from ....chat.choices.services import ChatChoicesOutputs
from ....chat.messages import SystemMessage
from ....chat.stream.services import ChatChoicesStreamRequest
from ....chat.stream.services import ChatChoicesStreamResponse
from ....chat.stream.services import static_check_is_chat_choices_stream_service
from ....chat.stream.types import AiChoiceDelta
from ....chat.stream.types import AiChoiceDeltas
from ....configs import Config
from ....resources import UseResources
from ....standard import ApiKey
from ....stream.services import new_stream_response
from .chat import AnthropicChatChoicesService
from .names import MODEL_NAMES


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='anthropic',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class AnthropicChatChoicesStreamService:
    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(AnthropicChatChoicesService.DEFAULT_MODEL_NAME)
            self._api_key = check.not_none(ApiKey.pop_secret(cc, env='ANTHROPIC_API_KEY'))

    READ_CHUNK_SIZE = 64 * 1024

    def invoke(
            self,
            request: ChatChoicesStreamRequest,
            *,
            max_tokens: int = 4096,  # FIXME: ChatOption
    ) -> ChatChoicesStreamResponse:
        messages = []
        system: str | None = None
        for i, m in enumerate(request.v):
            if isinstance(m, SystemMessage):
                if i != 0 or system is not None:
                    raise Exception('Only supports one system message and must be first')
                system = AnthropicChatChoicesService._get_msg_content(m)  # noqa
            else:
                messages.append(dict(
                    role=AnthropicChatChoicesService.ROLES_MAP[type(m)],  # noqa
                    content=check.isinstance(AnthropicChatChoicesService._get_msg_content(m), str),  # noqa
                ))

        raw_request = dict(
            model=MODEL_NAMES.resolve(self._model_name.v),
            **lang.opt_kw(system=system),
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )

        http_request = http.HttpRequest(
            'https://api.anthropic.com/v1/messages',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                b'x-api-key': self._api_key.reveal().encode('utf-8'),
                b'anthropic-version': b'2023-06-01',
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

                        # FIXME: https://docs.anthropic.com/en/docs/build-with-claude/streaming
                        for so in sd.process_line(l):
                            # FIXME: AnthropicSseMessageAssembler lol
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
                                    AiChoiceDelta(choice['delta'])
                                    for choice in sj['choices']
                                ]

                    if not b:
                        return []

            # raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))
            # return rh.build_response(raw_response)

            return new_stream_response(rs, yield_choices())
