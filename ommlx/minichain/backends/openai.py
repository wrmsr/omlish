import typing as ta

from omlish import check
from omlish import lang

from ..chat import AiMessage
from ..chat import ChatModel
from ..chat import Message
from ..chat import SystemMessage
from ..chat import ToolExecutionResultMessage
from ..chat import UserMessage
from ..content import Content
from ..content import Text
from ..embeddings import EmbeddingModel_
from ..prompts import Prompt
from ..prompts import PromptModel
from ..vectors import Vector


if ta.TYPE_CHECKING:
    import openai
else:
    openai = lang.proxy_import('openai')


class OpenaiPromptModel(PromptModel):
    model = 'gpt-3.5-turbo-instruct'

    def generate(self, t: PromptModel.Request[Prompt]) -> Response[str]:
        response = openai.completions.create(
            model=self.model,
            prompt=t.v.s,
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.,
            presence_penalty=0.,
            stream=False,
        )

        return Response(response.choices[0].text)


class OpenaiChatModel(ChatModel_):
    model = 'gpt-4o'

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
        ToolExecutionResultMessage: 'tool',
    }

    def _get_msg_content(self, m: Message) -> str:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return ''.join(check.isinstance(c, Text).s for c in m.content)

        else:
            raise TypeError(m)

    def generate(self, request: Request[ChatRequest]) -> Response[AiMessage]:
        response = openai.chat.completions.create(  # noqa
            model=self.model,
            messages=[
                dict(  # type: ignore
                    role=self.ROLES_MAP[type(m)],
                    content=self._get_msg_content(m),
                )
                for m in request.v.chat
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
        )

        return Response(AiMessage(response.choices[0].message.content))  # type: ignore


class OpenaiEmbeddingModel(EmbeddingModel_):
    model = 'text-embedding-3-small'

    def generate(self, request: Request[Content]) -> Response[Vector]:
        response = openai.embeddings.create(
            model=self.model,
            input=check.isinstance(request.v, Text).s,
        )

        return Response(Vector(response.data[0].embedding))
