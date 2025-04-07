import typing as ta

from omlish import cached
from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from ...chat.choices import AiChoice
from ...chat.messages import AiMessage
from ...chat.messages import Chat
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import ToolExecRequest
from ...chat.messages import ToolExecResultMessage
from ...chat.messages import UserMessage
from ...chat.services import ChatRequestOption
from ...chat.services import ChatResponse
from ...chat.tools import Tool
from ...chat.tools import ToolSpec
from ...llms import LlmRequestOption
from ...llms import MaxTokens
from ...llms import Temperature
from ...llms import TokenUsage
from ...llms import TokenUsageOutput
from ...services import RequestOption


##


def _opt_dct_fld(k, v):
    return {k: v} if v else {}


def render_tool_spec(ts: ToolSpec) -> ta.Mapping[str, ta.Any]:
    return dict(
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


def build_request_message(m: Message) -> ta.Mapping[str, ta.Any]:
    if isinstance(m, SystemMessage):
        return dict(
            role='system',
            content=m.s,
        )

    elif isinstance(m, AiMessage):
        return dict(
            role='assistant',
            content=m.s,
            **(dict(tool_calls=[
                dict(
                    id=te.id,
                    function=dict(
                        arguments=te.args,
                        name=te.spec.name,
                    ),
                    type='function',
                )
                for te in m.tool_exec_requests
            ]) if m.tool_exec_requests else {}),
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


##


class OpenaiChatRequestHandler:
    def __init__(
            self,
            chat: Chat,
            *options: ChatRequestOption | LlmRequestOption,
            model: str,
            mandatory_kwargs: ta.Mapping[str, ta.Any] | None = None,
    ) -> None:
        super().__init__()

        self._chat = chat
        self._options = options
        self._model = model
        self._mandatory_kwargs = mandatory_kwargs

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
        ToolExecResultMessage: 'tool',
    }

    DEFAULT_OPTIONS: ta.ClassVar[tv.TypedValues[RequestOption]] = tv.TypedValues(
        Temperature(0.),
        MaxTokens(1024),
    )

    _OPTION_KWARG_NAMES_MAP: ta.Mapping[type[tv.ScalarTypedValue], str] = {
        Temperature: 'temperature',
        MaxTokens: 'max_tokens',
    }

    class _ProcessedOptions(ta.NamedTuple):
        kwargs: dict[str, ta.Any]
        tools_by_name: dict[str, ToolSpec]

    @cached.function
    def _process_options(self) -> _ProcessedOptions:
        kwargs: dict = dict(
            temperature=0,
            max_tokens=1024,
        )

        tools_by_name: dict[str, ToolSpec] = {}

        for opt in self._options:
            if (
                    isinstance(opt, tv.ScalarTypedValue) and
                    (kwn := self._OPTION_KWARG_NAMES_MAP.get(type(opt))) is not None
            ):
                kwargs[kwn] = opt.v

            elif isinstance(opt, Tool):
                if opt.spec.name in tools_by_name:
                    raise NameError(opt.spec.name)
                tools_by_name[opt.spec.name] = opt.spec

            else:
                raise TypeError(opt)

        if (mk := self._mandatory_kwargs):
            for k, v in mk.items():
                check.not_in(k, kwargs)
                kwargs[k] = v

        return self._ProcessedOptions(
            kwargs=kwargs,
            tools_by_name=tools_by_name,
        )

    @cached.function
    def raw_request(self) -> ta.Mapping[str, ta.Any]:
        po = self._process_options()

        tools = [
            dict(
                type='function',
                function=render_tool_spec(ts),
            )
            for ts in po.tools_by_name.values()
        ]

        return dict(
            model=self._model,
            messages=[
                build_request_message(m)
                for m in self._chat
            ],
            top_p=1,
            **lang.opt_kw(tools=tools),
            frequency_penalty=0.0,
            presence_penalty=0.0,
            **po.kwargs,
        )

    def build_response(self, raw_response: ta.Mapping[str, ta.Any]) -> ChatResponse:
        po = self._process_options()

        return ChatResponse(
            [
                AiChoice(AiMessage(
                    choice['message']['content'],
                    tool_exec_requests=[
                        ToolExecRequest(
                            id=tc['id'],
                            spec=po.tools_by_name[tc['function']['name']],
                            args=tc['function']['arguments'],
                        )
                        for tc in choice['message'].get('tool_calls', [])
                    ],
                ))
                for choice in raw_response['choices']
            ],

            outputs=tv.TypedValues(
                *([TokenUsageOutput(TokenUsage(
                    input=tu['prompt_tokens'],
                    output=tu['completion_tokens'],
                    total=tu['total_tokens'],
                ))] if (tu := raw_response.get('usage')) is not None else []),
            ),
        )
