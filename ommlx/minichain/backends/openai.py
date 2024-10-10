import contextlib
import typing as ta

from omlish import check
from omlish import lang

from ..chat import AiMessage
from ..chat import ChatModel
from ..chat import ChatRequest
from ..chat import ChatRequestOptions
from ..chat import ChatResponse
from ..chat import Message
from ..chat import SystemMessage
from ..chat import ToolExecResultMessage
from ..chat import UserMessage
from ..generative import MaxTokens
from ..generative import Temperature
from ..models import TokenUsage
from ..options import Options
from ..options import ScalarOption
from ..prompts import PromptModel
from ..prompts import PromptRequest
from ..prompts import PromptResponse
from ..vectors import EmbeddingModel
from ..vectors import EmbeddingRequest
from ..vectors import EmbeddingResponse
from ..vectors import Vector


if ta.TYPE_CHECKING:
    import openai
    import openai.types.chat
else:
    openai = lang.proxy_import('openai')


class OpenaiPromptModel(PromptModel):
    model = 'gpt-3.5-turbo-instruct'

    def __init__(self, *, api_key: str | None = None) -> None:
        super().__init__()
        self._api_key = api_key

    def invoke(self, t: PromptRequest) -> PromptResponse:
        client = openai.OpenAI(
            api_key=self._api_key,
        )

        response = client.completions.create(
            model=self.model,
            prompt=t.v,
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.,
            presence_penalty=0.,
            stream=False,
        )

        return PromptResponse(v=response.choices[0].text)


class OpenaiChatModel(ChatModel):
    DEFAULT_MODEL = 'gpt-4o'

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
        ToolExecResultMessage: 'tool',
    }

    DEFAULT_OPTIONS: ta.ClassVar[Options[ChatRequestOptions]] = Options(
        Temperature(0.),
        MaxTokens(1024),
    )

    def __init__(
            self,
            *,
            model: str | None = None,
            api_key: str | None = None,
    ) -> None:
        super().__init__()
        self._model = model or self.DEFAULT_MODEL
        self._api_key = api_key

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    _OPTION_KWARG_NAMES_MAP: ta.Mapping[type[ScalarOption], str] = {
        Temperature: 'temperature',
        MaxTokens: 'max_tokens',
    }

    def invoke(self, request: ChatRequest) -> ChatResponse:
        kw: dict = dict(
            temperature=0,
            max_tokens=1024,
        )

        for opt in request.options:
            if isinstance(opt, ScalarOption) and (kwn := self._OPTION_KWARG_NAMES_MAP.get(type(opt))) is not None:
                kw[kwn] = opt.v

            else:
                raise TypeError(opt)

        with contextlib.closing(openai.OpenAI(
            api_key=self._api_key,
        )) as client:
            raw_response = client.chat.completions.create(  # noqa
                model=self._model,
                messages=[
                    dict(  # type: ignore
                        role=self.ROLES_MAP[type(m)],
                        content=self._get_msg_content(m),
                    )
                    for m in request.v
                ],
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stream=False,
                **kw,
            )

        response: 'openai.types.chat.chat_completion.ChatCompletion' = raw_response  # type: ignore  # noqa
        return ChatResponse(
            v=AiMessage(response.choices[0].message.content),
            usage=TokenUsage(
                input=response.usage.prompt_tokens,
                output=response.usage.completion_tokens,
                total=response.usage.total_tokens,
            ) if response.usage is not None else None,
        )


class OpenaiEmbeddingModel(EmbeddingModel):
    model = 'text-embedding-3-small'

    def __init__(self, *, api_key: str | None = None) -> None:
        super().__init__()
        self._api_key = api_key

    def invoke(self, request: EmbeddingRequest) -> EmbeddingResponse:
        client = openai.OpenAI(
            api_key=self._api_key,
        )

        response = client.embeddings.create(
            model=self.model,
            input=check.isinstance(request.v, str),
        )

        return EmbeddingResponse(v=Vector(response.data[0].embedding))
