"""
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
"""
import os
import typing as ta

from omlish import check
from omlish.formats import json
from omlish.http import all as http

from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import UserMessage
from ...chat.models import AiChoice
from ...chat.models import ChatModel
from ...chat.models import ChatRequest
from ...chat.models import ChatResponse


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='google', type='ChatModel')
class GoogleChatModel(ChatModel):
    model: ta.ClassVar[str] = (
        # 'gemini-1.5-flash-latest'
        'gemini-2.0-pro-exp-02-05'
    )

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    def __init__(self, *, api_key: str | None = None) -> None:
        super().__init__()
        self._api_key = api_key

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'

    def invoke(
            self,
            request: ChatRequest,
    ) -> ChatResponse:
        if not (key := self._api_key):
            key = os.environ['GEMINI_API_KEY']

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

        resp = http.request(
            f'{self.BASE_URL.rstrip("/")}/{self.model}:generateContent?key={key}',
            headers={'Content-Type': 'application/json'},
            data=json.dumps_compact(req_dct).encode('utf-8'),
            method='POST',
        )

        resp_dct = json.loads(check.not_none(resp.data).decode('utf-8'))

        return ChatResponse(v=[
            AiChoice(AiMessage(c['content']['parts'][0]['text']))
            for c in resp_dct['candidates']
        ])
