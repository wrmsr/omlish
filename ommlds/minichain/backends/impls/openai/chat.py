"""
TODO:
 - defaults:
   {
     "frequency_penalty": 0.0,
     "max_tokens": 64,
     "messages": ...,
     "model": "gpt-4o",
     "presence_penalty": 0.0,
     "temperature": 0.1,
     "top_p": 1
   }
"""
import typing as ta

from omlish import check
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http

from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....standard import ApiKey
from ....standard import DefaultOptions
from ....standard import ModelName
from .format import OpenaiChatRequestHandler


##


# @omlish-manifest $.minichain.registry.RegistryManifest(name='openai', type='ChatChoicesService')
@static_check_is_chat_choices_service
class OpenaiChatChoicesService:
    DEFAULT_MODEL_NAME: ta.ClassVar[str] = (
        'gpt-4o'
        # 'gpt-4o-mini'
    )

    def __init__(self, *configs: ApiKey | ModelName | DefaultOptions) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(ModelName(self.DEFAULT_MODEL_NAME))
            self._api_key = ApiKey.pop_secret(cc, env='OPENAI_API_KEY')
            self._default_options: tv.TypedValues = DefaultOptions.pop(cc)

    def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        # check.isinstance(request, ChatRequest)

        rh = OpenaiChatRequestHandler(
            request.v,
            *tv.TypedValues(
                *self._default_options,
                *request.options,
                override=True,
            ),
            model=self._model_name.v,
            mandatory_kwargs=dict(
                stream=False,
            ),
        )

        raw_request = rh.raw_request()

        http_response = http.request(
            'https://api.openai.com/v1/chat/completions',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))

        return rh.build_response(raw_response)
