"""
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
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
from ..content import Text


class GoogleChatModel(ChatModel):
    model: ta.ClassVar[str] = 'gemini-1.5-flash-latest'

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    def _get_msg_content(self, m: Message) -> str:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return ''.join(check.isinstance(c, Text).s for c in m.content)

        else:
            raise TypeError(m)

    BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'

    def invoke(
            self,
            request: ChatRequest,
    ) -> ChatResponse:
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

        with urllib.request.urlopen(urllib.request.Request(  # noqa
                f'{self.BASE_URL.rstrip("/")}/{self.model}:generateContent?key={key}',
                headers={'Content-Type': 'application/json'},
                data=json.dumps_compact(req_dct).encode('utf-8'),
                method='POST',
        )) as resp:
            resp_buf = resp.read()

        resp_dct = json.loads(resp_buf.decode('utf-8'))

        return ChatResponse(v=AiMessage(resp_dct['candidates'][0]['content']['parts'][0]['text']))
