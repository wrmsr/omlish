"""
https://platform.openai.com/docs/api-reference/responses-streaming
"""
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.http import sse

from .....backends.openai import protocol as pt
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.choices.stream.services import ChatChoicesStreamResponse
from ....chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ....chat.choices.stream.types import AiChoiceDeltas
from ....chat.choices.stream.types import AiChoicesDeltas
from ....chat.choices.stream.types import ChatChoicesStreamOption
from ....configs import Config
from ....http.stream import BytesHttpStreamResponseBuilder
from ....http.stream import SimpleSseLinesHttpStreamResponseHandler
from ....resources import ResourcesOption
from ....standard import ApiKey
from ....stream.services import StreamOption
from .chat import OpenaiChatChoicesService
from .format import OpenaiChatRequestHandler
from .format import build_mc_ai_delta
from .names import CHAT_MODEL_NAMES


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='openai',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class OpenaiChatChoicesStreamService:
    def __init__(
            self,
            *configs: Config,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(OpenaiChatChoicesService.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env='OPENAI_API_KEY')

    URL: ta.ClassVar[str] = 'https://api.openai.com/v1/chat/completions'

    def _process_sse(self, so: sse.SseDecoderOutput) -> ta.Sequence[AiChoicesDeltas | None]:
        if not (isinstance(so, sse.SseEvent) and so.type == b'message'):
            return []

        ss = so.data.decode('utf-8')
        if ss == '[DONE]':
            return [None]

        sj = json.loads(ss)  # ChatCompletionChunk

        check.state(sj['object'] == 'chat.completion.chunk')

        ccc = msh.unmarshal(sj, pt.ChatCompletionChunk)

        # FIXME: stop reason
        if not ccc.choices:
            return []

        if any(choice.finish_reason for choice in ccc.choices):
            check.state(all(choice.finish_reason for choice in ccc.choices))
            return [None]

        return [AiChoicesDeltas([
            AiChoiceDeltas([build_mc_ai_delta(choice.delta)])
            for choice in ccc.choices
        ])]

    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        rh = OpenaiChatRequestHandler(
            request.v,
            *[
                o
                for o in request.options
                if not isinstance(o, (ChatChoicesStreamOption, StreamOption, ResourcesOption))
            ],
            model=CHAT_MODEL_NAMES.resolve(self._model_name.v),
            mandatory_kwargs=dict(
                stream=True,
                stream_options=pt.ChatCompletionRequest.StreamOptions(
                    include_usage=True,
                ),
            ),
        )

        raw_request = msh.marshal(rh.oai_request())

        http_request = http.HttpRequest(
            self.URL,
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        return await BytesHttpStreamResponseBuilder(
            self._http_client,
            lambda http_response: SimpleSseLinesHttpStreamResponseHandler(self._process_sse).as_lines().as_bytes(),
            read_chunk_size=self.READ_CHUNK_SIZE,
        ).new_stream_response(
            http_request,
            request.options,
        )
