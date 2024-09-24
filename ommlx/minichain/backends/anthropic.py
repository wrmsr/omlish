import typing as ta

from omlish import check
from omlish import lang

from .. import Request
from .. import Response
from ..chat import AiMessage
from ..chat import ChatModel_
from ..chat import ChatRequest
from ..chat import Message
from ..chat import SystemMessage
from ..chat import UserMessage
from ..content import Text


if ta.TYPE_CHECKING:
    import anthropic
else:
    anthropic = lang.proxy_import('anthropic')


class AnthropicChatModel(ChatModel_):
    model: ta.ClassVar[str] = 'claude-3-opus-20240229'

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

    def generate(
            self,
            request: Request[ChatRequest],
            *,
            max_tokens: int = 4096,
    ) -> Response[AiMessage]:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=self.model,
            messages=[  # noqa
                dict(
                    role=self.ROLES_MAP[type(m)],  # type: ignore
                    content=self._get_msg_content(m),
                )
                for m in request.v.chat
            ],
            max_tokens=max_tokens,
        )
        return Response(AiMessage(response.content[0].text))  # type: ignore
