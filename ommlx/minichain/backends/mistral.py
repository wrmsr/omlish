"""
https://docs.mistral.ai/getting-started/models/
"""
import os
import typing as ta
import urllib.request

from omlish import check
from omlish.formats import json

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

    def _get_msg_content(self, m: Message) -> str:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return check.isinstance(m.content, str)

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

        with urllib.request.urlopen(urllib.request.Request(  # noqa
                'https://api.mistral.ai/v1/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {key}',
                },
                data=json.dumps_compact(req_dct).encode('utf-8'),
                method='POST',
        )) as resp:
            resp_buf = resp.read()

        resp_dct = json.loads(resp_buf.decode('utf-8'))

        return ChatResponse(v=AiMessage(resp_dct['choices'][0]['message']['content']))
