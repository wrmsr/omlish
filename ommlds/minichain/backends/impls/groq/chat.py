import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http

from .....backends.groq import protocol as pt
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.tools.types import Tool
from ....models.configs import ModelName
from ....standard import ApiKey
from ....standard import DefaultOptions
from .names import MODEL_NAMES
from .protocol import build_gq_request_messages
from .protocol import build_gq_request_tool
from .protocol import build_mc_choices_response


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='groq',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class GroqChatChoicesService:
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(MODEL_NAMES.default))

    def __init__(
            self,
            *configs: ApiKey | ModelName | DefaultOptions,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env='GROQ_API_KEY')
            self._default_options: tv.TypedValues = DefaultOptions.pop(cc)

    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        tools: list[pt.ChatCompletionRequest.Tool] = []
        with tv.TypedValues(*request.options).consume() as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(build_gq_request_tool(t))

        gq_request = pt.ChatCompletionRequest(
            messages=build_gq_request_messages(request.v),
            model=MODEL_NAMES.resolve(self._model_name.v),
            tools=tools or None,
        )

        raw_request = msh.marshal(gq_request)

        http_response = await http.async_request(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
            client=self._http_client,
        )

        raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))

        return build_mc_choices_response(msh.unmarshal(raw_response, pt.ChatCompletionResponse))
