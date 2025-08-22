"""
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
"""
import typing as ta

from omlish import check
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http

from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.types import AiChoice
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import UserMessage
from ....models.configs import ModelName
from ....standard import ApiKey
from .names import MODEL_NAMES


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='google',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class GoogleChatChoicesService:
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

    def invoke(
            self,
            request: ChatChoicesRequest,
    ) -> ChatChoicesResponse:
        key = check.not_none(self._api_key).reveal()

        req_dct = {
            'contents': [
                {
                    'role': self.ROLES_MAP[type(m)],
                    'parts': [
                        {
                            'text': self._get_msg_content(m),
                        },
                    ],
                }
                for m in request.v
            ],
        }

        model_name = MODEL_NAMES.resolve(self._model_name.v)

        resp = http.request(
            f'{self.BASE_URL.rstrip("/")}/{model_name}:generateContent?key={key}',
            headers={'Content-Type': 'application/json'},
            data=json.dumps_compact(req_dct).encode('utf-8'),
            method='POST',
        )

        resp_dct = json.loads(check.not_none(resp.data).decode('utf-8'))

        return ChatChoicesResponse([
            AiChoice(AiMessage(c['content']['parts'][0]['text']))
            for c in resp_dct['candidates']
        ])
