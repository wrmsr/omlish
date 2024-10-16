import contextlib
import typing as ta

from omlish import check
from omlish import lang

from ...chat import AiMessage
from ...chat import ChatModel
from ...chat import ChatRequest
from ...chat import ChatRequestOptions
from ...chat import ChatResponse
from ...chat import Message
from ...chat import SystemMessage
from ...chat import Tool
from ...chat import ToolExecRequest
from ...chat import ToolExecResultMessage
from ...chat import ToolSpec
from ...chat import UserMessage
from ...generative import MaxTokens
from ...generative import Temperature
from ...models import TokenUsage
from ...options import Options
from ...options import ScalarOption


if ta.TYPE_CHECKING:
    import openai
    import openai.types.chat
else:
    openai = lang.proxy_import('openai')


def _opt_dct_fld(k, v):
    return {k: v} if v else {}


def _render_tool_spec(td: ToolSpec) -> ta.Any:
    return {
        'type': 'function',
        'function': {
            'name': td.name,

            **_opt_dct_fld('description', td.desc),

            'parameters': {
                'type': 'object',
                'properties': {
                    tp.name: {
                        'type': tp.dtype,
                        **_opt_dct_fld('description', tp.desc),
                    }
                    for tp in td.params
                },

                'required': [tp.name for tp in td.params if tp.required],
                'additionalProperties': False,
            },
        },
    }


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

        tools: list = []

        for opt in request.options:
            if isinstance(opt, ScalarOption) and (kwn := self._OPTION_KWARG_NAMES_MAP.get(type(opt))) is not None:
                kw[kwn] = opt.v

            elif isinstance(opt, Tool):
                tools.append(_render_tool_spec(opt.spec))

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
                tools=tools,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stream=False,
                **kw,
            )

        response: 'openai.types.chat.chat_completion.ChatCompletion' = raw_response  # type: ignore  # noqa
        choice = check.single(response.choices)

        return ChatResponse(
            v=AiMessage(
                choice.message.content,
                tool_exec_requests=[
                    ToolExecRequest(
                        id=tc.id,
                        name=tc.function.name,
                        args=tc.function.arguments,
                    )
                    for tc in choice.message.tool_calls or []
                ],
            ),
            usage=TokenUsage(
                input=response.usage.prompt_tokens,
                output=response.usage.completion_tokens,
                total=response.usage.total_tokens,
            ) if response.usage is not None else None,
        )
