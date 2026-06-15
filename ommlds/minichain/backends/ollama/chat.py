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

https://github.com/ollama/ollama/blob/main/docs/api.md
"""
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats.json import all as json
from omlish.http import all as http

from ....backends.ollama import protocol as pt
from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.stream.choices.services import ChatChoicesStreamRequest
from ...chat.stream.choices.types import ChatChoicesStreamOption
from ...chat.tools.types import Tool
from ...events.types import EventCallback
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceResponseEvent
from ...http.stream import HttpStreamResponseError
from ...models.configs import ModelName
from ...resources import ResourcesOption
from ...services import StreamOption
from ...standard import ApiUrl
from .protocol import build_mc_choices_response
from .protocol import build_ol_request_messages
from .protocol import build_ol_request_tool


##


# @omlish-manifest $.minichain.specs.manifests.BackendStringsManifest(
#     [
#         'ChatChoicesService',
#         'ChatChoicesStreamService',
#     ],
#     'ollama',
# )


##


class BaseOllamaChatChoicesService(lang.Abstract):
    """
    Shared config consumption and request building for ollama's native (JSONL, no-auth) chat api.

    Note: ollama also exposes an openai-compatible `/v1/chat/completions` endpoint - that one is served by the
    openai-compat dialect core, not this. This is ollama's *native* `/api/chat` (typed thinking, JSONL stream).
    """

    DEFAULT_API_URL: ta.ClassVar[ApiUrl] = ApiUrl('http://localhost:11434/api')
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName('gemma4:12b-mlx')  # FIXME: they broke non-mlx models lol

    def __init__(
            self,
            *configs: ApiUrl | ModelName,
            http_client: http.AsyncHttpClient | None = None,
            on_event: EventCallback | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client
        self._on_event = on_event

        with tv.consume(*configs) as cc:
            self._api_url = cc.pop(self.DEFAULT_API_URL)
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)

    #

    def _chat_url(self) -> str:
        return self._api_url.v.removesuffix('/') + '/chat'

    def _build_request(
            self,
            request: ChatChoicesRequest | ChatChoicesStreamRequest,
            *,
            stream: bool = False,
    ) -> pt.ChatRequest:
        messages = build_ol_request_messages(request.v)

        tools: list[pt.Tool] = []
        with tv.consume(*[
            o
            for o in request.options
            if not isinstance(o, (ChatChoicesStreamOption, StreamOption, ResourcesOption))
        ]) as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(build_ol_request_tool(t))

        return pt.ChatRequest(
            model=self._model_name.v.replace('--', '/'),
            messages=messages,
            tools=tools or None,
            stream=stream,
        )


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='ollama',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class OllamaChatChoicesService(BaseOllamaChatChoicesService):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        a_req = self._build_request(request)

        raw_request = msh.marshal(a_req)

        if self._on_event is not None:
            await self._on_event(ExternalServiceRequestEvent(
                service=self,
                request=raw_request,
            ))

        http_response = await http.async_request(
            self._chat_url(),
            data=json.dumps(raw_request).encode('utf-8'),
            client=self._http_client,
        )

        if http_response.status != 200:
            raise HttpStreamResponseError(http_response, data=http_response.data)

        json_response = json.loads(check.not_none(http_response.data).decode('utf-8'))

        if self._on_event is not None:
            await self._on_event(ExternalServiceResponseEvent(
                service=self,
                response=json_response,
            ))

        return build_mc_choices_response(msh.unmarshal(json_response, pt.ChatResponse))
