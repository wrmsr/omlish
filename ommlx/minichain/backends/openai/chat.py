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
import os
import typing as ta

from omlish import check
from omlish.formats import json
from omlish.http import all as http
from omlish.secrets.secrets import Secret

from ...chat.services import ChatRequest
from ...chat.services import ChatResponse
from ...chat.services import ChatService
from .format import OpenaiChatRequestHandler


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='openai', type='ChatService')
class OpenaiChatService(
    ChatService[
        ChatRequest,
        ChatResponse,
    ],
    request=ChatRequest,
    response=ChatResponse,
):
    DEFAULT_MODEL: ta.ClassVar[str] = (
        'gpt-4o'
        # 'gpt-4o-mini'
    )

    def __init__(
            self,
            *,
            model: str | None = None,
            api_key: Secret | str | None = None,
    ) -> None:
        super().__init__()

        self._model = model or self.DEFAULT_MODEL
        self._api_key = self._default_api_key(api_key)

    @classmethod
    def _default_api_key(cls, api_key: Secret | str | None = None) -> Secret:
        return Secret.of(api_key if api_key is not None else os.environ['OPENAI_API_KEY'])

    def invoke(self, request: ChatRequest) -> ChatResponse:
        check.isinstance(request, ChatRequest)

        rh = OpenaiChatRequestHandler(
            request.chat,
            *request.options,
            model=self._model,
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
