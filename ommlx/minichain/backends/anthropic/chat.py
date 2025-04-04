"""
https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table

https://github.com/anthropics/anthropic-sdk-python/tree/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/types
https://github.com/anthropics/anthropic-sdk-python/blob/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/resources/completions.py#L53
https://github.com/anthropics/anthropic-sdk-python/blob/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/resources/messages.py#L70
"""
import os
import typing as ta

from omlish import check
from omlish import lang
from omlish.formats import json
from omlish.http import all as http
from omlish.secrets.secrets import Secret

from ...chat.choices import AiChoice
from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import UserMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatResponse
from ...chat.services import ChatService


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='anthropic', type='ChatService')
class AnthropicChatService(ChatService):
    model: ta.ClassVar[str] = (
        'claude-3-5-sonnet-20241022'
        # 'claude-3-opus-20240229'
    )

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    def __init__(
            self,
            *,
            api_key: Secret | str | None = None,
    ) -> None:
        super().__init__()
        self._api_key = Secret.of(api_key if api_key is not None else os.environ['ANTHROPIC_API_KEY'])

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
            *,
            max_tokens: int = 4096,  # FIXME: ChatRequestOption
    ) -> ChatResponse:
        messages = []
        system: str | None = None
        for i, m in enumerate(request.chat):
            if isinstance(m, SystemMessage):
                if i != 0 or system is not None:
                    raise Exception('Only supports one system message and must be first')
                system = self._get_msg_content(m)
            else:
                messages.append(dict(
                    role=self.ROLES_MAP[type(m)],  # noqa
                    content=check.isinstance(self._get_msg_content(m), str),
                ))

        raw_request = dict(
            model=self.model,
            **lang.opt_kw(system=system),
            messages=messages,
            max_tokens=max_tokens,
        )

        raw_response = http.request(
            'https://api.anthropic.com/v1/messages',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                b'x-api-key': self._api_key.reveal().encode('utf-8'),
                b'anthropic-version': b'2023-06-01',
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        response = json.loads(check.not_none(raw_response.data).decode('utf-8'))

        return ChatResponse([
            AiChoice(AiMessage(response['content'][0]['text'])),  # noqa
        ])
