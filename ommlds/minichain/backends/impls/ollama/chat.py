"""
devstral-small-2:24b
dolphin3:latest
fauxpaslife/nanbeige4.1:latest
functiongemma:270m
gemma3:27b
gemma3:4b
glm-4.7-flash:q8_0
llama3.2:1b
llama3.2:latest
ministral-3:14b
mistral:latest
nemotron-3-nano:30b
olmo-3.1:32b-instruct
olmo-3.1:32b-think
phi4-mini:latest
qwen3-coder-next:latest
qwen3-coder:30b
qwen3-next:80b
qwen3:30b
qwen3:32b
qwen3.5:0.8b
qwen3.5:122b
qwen3.5:2b
qwen3.5:35b
qwen3.5:4b
qwen3.5:9b
"""
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.io.streams.framing import LongestMatchDelimiterByteStreamFrameDecoder
from omlish.io.streams.scanning import ScanningByteStreamBuffer
from omlish.io.streams.segmented import SegmentedByteStreamBuffer

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
            model=self._model_name.v.replace('--', '/'),
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
            model=self._model_name.v.replace('--', '/'),
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
                buf = ScanningByteStreamBuffer(SegmentedByteStreamBuffer(chunk_size=0x4000))
                frm = LongestMatchDelimiterByteStreamFrameDecoder([b'\r', b'\n', b'\r\n'])
                while True:
                    b = await http_response.stream.read1(self.READ_CHUNK_SIZE)
                    buf.write(b)
                    for l in frm.decode(buf, final=not b):
                        lj = json.loads(l.tobytes().decode('utf-8'))
                        lp: pt.ChatResponse = msh.unmarshal(lj, pt.ChatResponse)

                        if (ds := build_mc_ai_choice_deltas(lp)).deltas:
                            await sink.emit(AiChoicesDeltas([ds]))

                    if not b:
                        check.state(not len(buf))

                        return []

            return await new_stream_response(rs, inner)
