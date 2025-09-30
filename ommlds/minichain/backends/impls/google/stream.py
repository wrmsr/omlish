"""
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
"""
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.io.buffers import DelimitingBuffer

from .....backends.google.protocol import types as pt
from ....chat.choices.types import ChatChoicesOutputs
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import UserMessage
from ....chat.stream.services import ChatChoicesStreamRequest
from ....chat.stream.services import ChatChoicesStreamResponse
from ....chat.stream.services import static_check_is_chat_choices_stream_service
from ....chat.stream.types import AiChoiceDeltas
from ....chat.stream.types import AiChoicesDeltas
from ....chat.stream.types import ContentAiChoiceDelta
from ....models.configs import ModelName
from ....resources import UseResources
from ....standard import ApiKey
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response
from .names import MODEL_NAMES


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='google',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class GoogleChatChoicesStreamService:
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(MODEL_NAMES.default))

    def __init__(self, *configs: ApiKey | ModelName) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env='GEMINI_API_KEY')

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, AiMessage):
            return check.isinstance(m.c, str)

        elif isinstance(m, (SystemMessage, UserMessage)):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    BASE_URL: ta.ClassVar[str] = 'https://generativelanguage.googleapis.com/v1beta/models'

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    READ_CHUNK_SIZE = 64 * 1024

    async def invoke(
            self,
            request: ChatChoicesStreamRequest,
    ) -> ChatChoicesStreamResponse:
        key = check.not_none(self._api_key).reveal()

        g_req = pt.GenerateContentRequest(
            contents=[
                pt.Content(
                    parts=[pt.Part(
                        text=check.not_none(self._get_msg_content(m)),
                    )],
                    role=self.ROLES_MAP[type(m)],  # type: ignore[arg-type]
                )
                for m in request.v
            ],
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
            http_client = rs.enter_context(http.client())
            http_response = rs.enter_context(http_client.stream_request(http_request))

            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs] | None:
                db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
                while True:
                    # FIXME: read1 not on response stream protocol
                    b = http_response.stream.read1(self.READ_CHUNK_SIZE)  # type: ignore[attr-defined]
                    for bl in db.feed(b):
                        if isinstance(bl, DelimitingBuffer.Incomplete):
                            # FIXME: handle
                            return []
                        l = bl.decode('utf-8')
                        if not l:
                            continue
                        if l.startswith('data: '):
                            gcr = msh.unmarshal(json.loads(l[6:]), pt.GenerateContentResponse)  # noqa
                            cnd = check.single(check.not_none(gcr.candidates))
                            for p in check.not_none(cnd.content).parts or []:
                                await sink.emit(AiChoicesDeltas([
                                    AiChoiceDeltas([
                                        ContentAiChoiceDelta(check.not_none(p.text)),
                                    ]),
                                ]))

                    if not b:
                        return []

            return await new_stream_response(rs, inner)
