"""
https://docs.anthropic.com/en/docs/about-claude/models#model-comparison-table
"""
import typing as ta

from omlish import check
from omlish import lang

from ..chat import AiChoice
from ..chat import AiMessage
from ..chat import ChatModel
from ..chat import ChatRequest
from ..chat import ChatResponse
from ..chat import Message
from ..chat import SystemMessage
from ..chat import UserMessage


if ta.TYPE_CHECKING:
    import anthropic
else:
    anthropic = lang.proxy_import('anthropic')


class AnthropicChatModel(ChatModel):
    model: ta.ClassVar[str] = (
        'claude-3-5-sonnet-20241022'
        # 'claude-3-opus-20240229'
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

    def invoke(
            self,
            request: ChatRequest,
            *,
            max_tokens: int = 4096,
    ) -> ChatResponse:
        client = anthropic.Anthropic(
            api_key=self._api_key,
        )

        messages = []
        system: str | None = None
        for i, m in enumerate(request.v):
            if isinstance(m, SystemMessage):
                if i != 0 or system is not None:
                    raise Exception('Only supports one system message and must be first')
                system = self._get_msg_content(m)
            else:
                messages.append(dict(
                    role=self.ROLES_MAP[type(m)],  # noqa
                    content=check.isinstance(self._get_msg_content(m), str),
                ))

        response = client.messages.create(  # noqa
            model=self.model,
            **(dict(system=system) if system is not None else {}),
            messages=messages,  # type: ignore
            max_tokens=max_tokens,
        )

        return ChatResponse(v=[
            AiChoice(AiMessage(response.content[0].text)),  # noqa
        ])
