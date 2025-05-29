"""
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
"""
import typing as ta

from omlish import check
from omlish.formats import json
from omlish.http import all as http

from ...chat.choices import AiChoice
from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import UserMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatResponse
from ...chat.services import ChatService
from ...configs import consume_configs
from ...standard import ApiKey
from ...standard import ModelName


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(name='google', type='ChatService')
class GoogleChatService(ChatService):
    DEFAULT_MODEL_NAME: ta.ClassVar[str] = (
        'gemini-2.0-flash'
    )

    def __init__(self, *configs: ApiKey | ModelName) -> None:
        super().__init__()

        with consume_configs(*configs) as cc:
            self._model_name = cc.pop(ModelName(self.DEFAULT_MODEL_NAME))
            self._api_key = ApiKey.pop_secret(cc, env='GEMINI_API_KEY')

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    def invoke(
            self,
            request: ChatRequest,
    ) -> ChatResponse:
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
                for m in request.chat
            ],
        }

        resp = http.request(
            f'{self.BASE_URL.rstrip("/")}/{self._model_name.v}:generateContent?key={key}',
            headers={'Content-Type': 'application/json'},
            data=json.dumps_compact(req_dct).encode('utf-8'),
            method='POST',
        )

        resp_dct = json.loads(check.not_none(resp.data).decode('utf-8'))

        return ChatResponse([
            AiChoice(AiMessage(c['content']['parts'][0]['text']))
            for c in resp_dct['candidates']
        ])
