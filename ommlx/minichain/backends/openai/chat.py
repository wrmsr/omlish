"""
TODO:
 - defaults:
   {
     "frequency_penalty": 0.0,
     "max_tokens": 64,
     "messages": ...,
     "model": "gpt-4o",
     "presence_penalty": 0.0,
     "temperature": 0.1,
     "top_p": 1
   }
"""
import contextlib
import typing as ta

from omlish import check
from omlish import lang
from omlish.secrets import Secret

from ...chat import AiChoice
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


def _render_tool_spec(ts: ToolSpec) -> 'openai.types.FunctionDefinition':
    return dict(  # type: ignore
        name=ts.name,

        **_opt_dct_fld('description', ts.desc),

        parameters=dict(
            type='object',
            properties={
                tp.name: {
                    'type': tp.dtype,
                    **_opt_dct_fld('description', tp.desc),
                }
                for tp in ts.params
            },

            required=[tp.name for tp in ts.params if tp.required],
            additionalProperties=False,
        ),
    )


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
            api_key: Secret | str | None = None,
    ) -> None:
        super().__init__()
        self._model = model or self.DEFAULT_MODEL
        self._api_key = Secret.of(api_key) if api_key is not None else None

    def _build_req_msg(self, m: Message) -> 'openai.types.chat.ChatCompletionMessageParam':
        if isinstance(m, SystemMessage):
            return dict(
                role='system',
                content=m.s,
            )

        elif isinstance(m, AiMessage):
            return dict(
                role='assistant',
                content=m.s,
                **(dict(tool_calls=[  # type: ignore
                    dict(
                        id=te.id,
                        function=dict(
                            arguments=te.args,
                            name=te.spec.name,
                        ),
                        type='function',
                    )
                    for te in m.tool_exec_requests
                ]) if m.tool_exec_requests else {}),  # type: ignore
            )

        elif isinstance(m, UserMessage):
            return dict(
                role='user',
                content=check.isinstance(m.c, str),
            )

        elif isinstance(m, ToolExecResultMessage):
            return dict(
                role='tool',
                tool_call_id=m.id,
                content=m.s,
            )

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

        tools_by_name: dict[str, ToolSpec] = {}

        for opt in request.options:
            if isinstance(opt, ScalarOption) and (kwn := self._OPTION_KWARG_NAMES_MAP.get(type(opt))) is not None:
                kw[kwn] = opt.v

            elif isinstance(opt, Tool):
                if opt.spec.name in tools_by_name:
                    raise NameError(opt.spec.name)
                tools_by_name[opt.spec.name] = opt.spec

            else:
                raise TypeError(opt)

        tools = [
            dict(
                type='function',
                function=_render_tool_spec(ts),
            )
            for ts in tools_by_name.values()
        ]

        with contextlib.closing(openai.OpenAI(
                api_key=Secret.of(self._api_key).reveal() if self._api_key is not None else None,
        )) as client:
            raw_request = dict(
                model=self._model,
                messages=[
                    self._build_req_msg(m)
                    for m in request.v
                ],
                top_p=1,
                **(dict(tools=tools) if tools else {}),
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stream=False,
                **kw,
            )
            raw_response = client.chat.completions.create(**raw_request)

        response: 'openai.types.chat.ChatCompletion' = raw_response  # noqa

        return ChatResponse(
            v=[
                AiChoice(AiMessage(
                    choice.message.content,
                    tool_exec_requests=[
                        ToolExecRequest(
                            id=tc.id,
                            spec=tools_by_name[tc.function.name],
                            args=tc.function.arguments,
                        )
                        for tc in choice.message.tool_calls or []
                    ],
                ))
                for choice in response.choices
            ],
            usage=TokenUsage(
                input=response.usage.prompt_tokens,
                output=response.usage.completion_tokens,
                total=response.usage.total_tokens,
            ) if response.usage is not None else None,
        )
