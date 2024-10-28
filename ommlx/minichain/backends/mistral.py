"""
https://docs.mistral.ai/getting-started/models/
"""
import os
import typing as ta

from omlish import check
from omlish import http
from omlish.formats import json

from ..chat import AiChoice
from ..chat import AiMessage
from ..chat import ChatModel
from ..chat import ChatRequest
from ..chat import ChatResponse
from ..chat import Message
from ..chat import SystemMessage
from ..chat import UserMessage


class MistralChatModel(ChatModel):
    model: ta.ClassVar[str] = 'mistral-large-latest'

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

    def invoke(
            self,
            request: ChatRequest,
    ) -> ChatResponse:
        if not (key := self._api_key):
            key = os.environ['MISTRAL_API_KEY']

        req_dct = {
            'model': self.model,
            'messages': [
                {
                    'role': self.ROLES_MAP[type(m)],
                    'content': self._get_msg_content(m),
                }
                for m in request.v
            ],
        }

        resp = http.request(
            'https://api.mistral.ai/v1/chat/completions',
            method='POST',
            data=json.dumps_compact(req_dct).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {key}',
            },
        )

        resp_dct = json.loads(check.not_none(resp.data).decode('utf-8'))

        return ChatResponse(v=[
            AiChoice(AiMessage(c['message']['content']))
            for c in resp_dct['choices']
        ])
