"""https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models"""
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats.json import all as json
from omlish.http import all as http

from ....backends.google.protocol import types as pt
from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.stream.services import ChatChoicesStreamRequest
from ...chat.tools.types import Tool
from ...events.types import EventCallback
from ...external import ExternalServiceRequestEvent
from ...external import ExternalServiceResponseEvent
from ...http.stream import HttpStreamResponseError
from ...models.configs import ModelName
from ...standard import ApiKey
from .names import MODEL_NAMES
from .protocol import build_g_request_content
from .protocol import build_g_request_tool
from .protocol import build_mc_choices_response
from .protocol import pop_g_system_instruction


##


class BaseGoogleChatChoicesService(lang.Abstract):
    """Shared config consumption, url/request building for the google generativelanguage (gemini) backend."""

    BASE_URL: ta.ClassVar[str] = 'https://generativelanguage.googleapis.com/v1beta/models'
    API_KEY_ENV: ta.ClassVar[str] = 'GEMINI_API_KEY'

    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(MODEL_NAMES.default))

    def __init__(
            self,
            *configs: ApiKey | ModelName,
            http_client: http.AsyncHttpClient | None = None,
            on_event: EventCallback | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client
        self._on_event = on_event

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env=self.API_KEY_ENV)

    #

    def _build_url(self, method: str, *, query: str = '') -> str:
        key = check.not_none(self._api_key).reveal()
        model_name = MODEL_NAMES.resolve(self._model_name.v)
        q = f'{query}&key={key}' if query else f'key={key}'
        return f'{self.BASE_URL.rstrip("/")}/{model_name}:{method}?{q}'

    def _build_request(self, request: ChatChoicesRequest | ChatChoicesStreamRequest) -> pt.GenerateContentRequest:
        g_tools: list[pt.Tool] = []
        with tv.consume(*request.options) as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                g_tools.append(build_g_request_tool(t))

        msgs = list(request.v)
        system_inst = pop_g_system_instruction(msgs)

        return pt.GenerateContentRequest(
            contents=[build_g_request_content(m) for m in msgs] or None,
            tools=g_tools or None,
            system_instruction=system_inst,
        )


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='google',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class GoogleChatChoicesService(BaseGoogleChatChoicesService):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        g_req = self._build_request(request)

        req_dct = msh.marshal(g_req)

        if self._on_event is not None:
            await self._on_event(ExternalServiceRequestEvent(
                service=self,
                request=req_dct,
            ))

        http_response = await http.async_request(
            self._build_url('generateContent'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps_compact(req_dct).encode('utf-8'),
            method='POST',
            client=self._http_client,
        )

        if http_response.status != 200:
            raise HttpStreamResponseError(http_response, data=http_response.data)

        resp_dct = json.loads(check.not_none(http_response.data).decode('utf-8'))

        if self._on_event is not None:
            await self._on_event(ExternalServiceResponseEvent(
                service=self,
                response=resp_dct,
            ))

        return build_mc_choices_response(msh.unmarshal(resp_dct, pt.GenerateContentResponse))
