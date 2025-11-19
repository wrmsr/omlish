import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.io.buffers import DelimitingBuffer

from .....backends.ollama import protocol as pt
from ....chat.choices.services import ChatChoicesOutputs
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.choices.stream.services import ChatChoicesStreamResponse
from ....chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ....chat.choices.stream.types import AiChoiceDeltas
from ....chat.choices.stream.types import AiChoicesDeltas
from ....chat.choices.types import AiChoice
from ....chat.messages import AiMessage
from ....chat.messages import AnyAiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import UserMessage
from ....chat.stream.types import ContentAiDelta
from ....models.configs import ModelName
from ....resources import UseResources
from ....standard import ApiUrl
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response


##


# @omlish-manifest $.minichain.backends.strings.manifests.BackendStringsManifest(
#     [
#         'ChatChoicesService',
#         'ChatChoicesStreamService',
#     ],
#     'ollama',
# )


##


class BaseOllamaChatChoicesService(lang.Abstract):
    DEFAULT_API_URL: ta.ClassVar[ApiUrl] = ApiUrl('http://localhost:11434/api')
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName('llama3.2')

    def __init__(
            self,
            *configs: ApiUrl | ModelName,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._api_url = cc.pop(self.DEFAULT_API_URL)
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)

    #

    ROLE_MAP: ta.ClassVar[ta.Mapping[type[Message], pt.Role]] = {  # noqa
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    @classmethod
    def _get_message_content(cls, m: Message) -> str | None:
        if isinstance(m, (AiMessage, UserMessage, SystemMessage)):
            return check.isinstance(m.c, str)
        else:
            raise TypeError(m)

    @classmethod
    def _build_request_messages(cls, mc_msgs: ta.Iterable[Message]) -> ta.Sequence[pt.Message]:
        messages: list[pt.Message] = []
        for m in mc_msgs:
            messages.append(pt.Message(
                role=cls.ROLE_MAP[type(m)],
                content=cls._get_message_content(m),
            ))
        return messages


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='ollama',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class OllamaChatChoicesService(BaseOllamaChatChoicesService):
    async def invoke(
            self,
            request: ChatChoicesRequest,
    ) -> ChatChoicesResponse:
        messages = self._build_request_messages(request.v)

        a_req = pt.ChatRequest(
            model=self._model_name.v,
            messages=messages,
            # tools=tools or None,
            stream=False,
        )

        raw_request = msh.marshal(a_req)

        async with http.manage_async_client(self._http_client) as http_client:
            raw_response = await http_client.request(http.HttpRequest(
                self._api_url.v.removesuffix('/') + '/chat',
                data=json.dumps(raw_request).encode('utf-8'),
            ))

        json_response = json.loads(check.not_none(raw_response.data).decode('utf-8'))

        resp = msh.unmarshal(json_response, pt.ChatResponse)

        out: list[AnyAiMessage] = []
        if resp.message.role == 'assistant':
            out.append(AiMessage(
                check.not_none(resp.message.content),
            ))
        else:
            raise TypeError(resp.message.role)

        return ChatChoicesResponse([
            AiChoice(out),
        ])


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='ollama',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class OllamaChatChoicesStreamService(BaseOllamaChatChoicesService):
    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def invoke(
            self,
            request: ChatChoicesStreamRequest,
    ) -> ChatChoicesStreamResponse:
        messages = self._build_request_messages(request.v)

        a_req = pt.ChatRequest(
            model=self._model_name.v,
            messages=messages,
            # tools=tools or None,
            stream=True,
        )

        raw_request = msh.marshal(a_req)

        http_request = http.HttpRequest(
            self._api_url.v.removesuffix('/') + '/chat',
            data=json.dumps(raw_request).encode('utf-8'),
        )

        async with UseResources.or_new(request.options) as rs:
            http_client = await rs.enter_async_context(http.manage_async_client(self._http_client))
            http_response = await rs.enter_async_context(await http_client.stream_request(http_request))

            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs] | None:
                db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
                while True:
                    b = await http_response.stream.read1(self.READ_CHUNK_SIZE)
                    for l in db.feed(b):
                        if isinstance(l, DelimitingBuffer.Incomplete):
                            # FIXME: handle
                            return []

                        lj = json.loads(l.decode('utf-8'))
                        lp: pt.ChatResponse = msh.unmarshal(lj, pt.ChatResponse)

                        check.state(lp.message.role == 'assistant')
                        check.none(lp.message.tool_name)
                        check.state(not lp.message.tool_calls)

                        if (c := lp.message.content):
                            await sink.emit(AiChoicesDeltas([AiChoiceDeltas([ContentAiDelta(
                                c,
                            )])]))

                    if not b:
                        return []

            return await new_stream_response(rs, inner)
