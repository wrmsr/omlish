"""
dolphin3:latest           d5ab9ae8e1f2    4.9 GB    11 months ago (no tools)

functiongemma:270m        7c19b650567a    300 MB    5 minutes ago
gemma3:27b                a418f5838eaf    17 GB     7 weeks ago (no tools)
gemma3:4b                 a2af6cc3eb7f    3.3 GB    7 weeks ago (no tools)

llama3.2:1b               baf6a787fdff    1.3 GB    13 months ago (too stupid for tools)
llama3.2:latest           a80c4f17acd5    2.0 GB    13 months ago

devstral-small-2:24b      24277f07f62d    15 GB     15 hours ago
ministral-3:14b           4760c35aeb9d    9.1 GB    11 hours ago
mistral:latest            6577803aa9a0    4.4 GB    3 seconds ago

nemotron-3-nano:30b       b725f1117407    24 GB     15 hours ago

olmo-3.1:32b-instruct     a16b6a5be6cf    19 GB     11 hours ago (no tools)
olmo-3.1:32b-think        223d4ec84d91    19 GB     11 hours ago (no tools)

phi4-mini:latest          78fad5d182a7    2.5 GB    8 months ago (no tools)

qwen3-coder:30b           06c1097efce0    18 GB     11 hours ago
qwen3-next:80b            b2ebb986e4e9    50 GB     11 hours ago
qwen3:30b                 ad815644918f    18 GB     11 hours ago
qwen3:32b                 030ee887880f    20 GB     11 hours ago
"""
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
from ....chat.choices.stream.types import AiChoicesDeltas
from ....chat.tools.types import Tool
from ....models.configs import ModelName
from ....resources import UseResources
from ....standard import ApiUrl
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response
from .protocol import build_mc_ai_choice_deltas
from .protocol import build_mc_choices_response
from .protocol import build_ol_request_messages
from .protocol import build_ol_request_tool


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
        messages = build_ol_request_messages(request.v)

        tools: list[pt.Tool] = []
        with tv.TypedValues(*request.options).consume() as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(build_ol_request_tool(t))

        a_req = pt.ChatRequest(
            model=self._model_name.v,
            messages=messages,
            tools=tools or None,
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

        return build_mc_choices_response(resp)


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
        messages = build_ol_request_messages(request.v)

        tools: list[pt.Tool] = []
        with tv.TypedValues(*request.options).consume() as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(build_ol_request_tool(t))

        a_req = pt.ChatRequest(
            model=self._model_name.v,
            messages=messages,
            tools=tools or None,
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

                        if (ds := build_mc_ai_choice_deltas(lp)).deltas:
                            await sink.emit(AiChoicesDeltas([ds]))

                    if not b:
                        return []

            return await new_stream_response(rs, inner)
