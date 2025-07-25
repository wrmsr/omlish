import typing as ta

from omlish import cached
from omlish import check
from omlish import lang
from omlish import typedvalues as tv
from omlish.formats import json

from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.types import AiChoice
from ...chat.choices.types import ChatChoicesOptions
from ...chat.messages import AiMessage
from ...chat.messages import Chat
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import ToolExecResultMessage
from ...chat.messages import UserMessage
from ...chat.stream.types import AiMessageDelta
from ...chat.tools import Tool
from ...content.prepare import prepare_content_str
from ...llms.types import MaxTokens
from ...llms.types import Temperature
from ...llms.types import TokenUsage
from ...llms.types import TokenUsageOutput
from ...tools.jsonschema import build_tool_spec_json_schema
from ...tools.types import ToolExecRequest
from ...tools.types import ToolSpec
from ...types import Option


##


def build_request_message(m: Message) -> ta.Mapping[str, ta.Any]:
    if isinstance(m, SystemMessage):
        return dict(
            role='system',
            content=m.c,
        )

    elif isinstance(m, AiMessage):
        return dict(
            role='assistant',
            content=m.s,
            **(dict(tool_calls=[
                dict(
                    id=te.id,
                    function=dict(
                        arguments=check.not_none(te.raw_args),
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
            content=prepare_content_str(m.c),
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
            *options: ChatChoicesOptions,
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

    DEFAULT_OPTIONS: ta.ClassVar[tv.TypedValues[Option]] = tv.TypedValues(
        Temperature(0.),
        MaxTokens(1024),
    )

    _OPTION_KWARG_NAMES_MAP: ta.ClassVar[ta.Mapping[str, type[ChatChoicesOptions]]] = dict(
        temperature=Temperature,
        max_tokens=MaxTokens,
    )

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

        with tv.TypedValues(*self._options).consume() as oc:
            kwargs.update(oc.pop_scalar_kwargs(**self._OPTION_KWARG_NAMES_MAP))

            for t in oc.pop(Tool, []):
                if t.spec.name in tools_by_name:
                    raise NameError(t.spec.name)
                tools_by_name[check.non_empty_str(t.spec.name)] = t.spec

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
                function=build_tool_spec_json_schema(ts),
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

    def build_ai_message(self, message: ta.Mapping[str, ta.Any]) -> AiMessage:
        return AiMessage(
            message.get('content'),
            tool_exec_requests=[
                ToolExecRequest(
                    id=tc['id'],
                    spec=self._process_options().tools_by_name[tc['function']['name']],
                    args=json.loads(tc['function']['arguments'] or '{}'),
                    raw_args=tc['function']['arguments'],
                )
                for tc in message.get('tool_calls', [])
            ] or None,
        )

    def build_response(self, raw_response: ta.Mapping[str, ta.Any]) -> ChatChoicesResponse:
        return ChatChoicesResponse(
            [
                AiChoice(self.build_ai_message(choice['message']))
                for choice in raw_response['choices']
            ],

            tv.TypedValues(
                *([TokenUsageOutput(TokenUsage(
                    input=tu['prompt_tokens'],
                    output=tu['completion_tokens'],
                    total=tu['total_tokens'],
                ))] if (tu := raw_response.get('usage')) is not None else []),
            ),
        )

    def build_ai_message_delta(self, delta: ta.Mapping[str, ta.Any]) -> AiMessageDelta:
        return AiMessageDelta(
            delta.get('content'),
            # FIXME:
            # tool_exec_requests=[
            #     ToolExecRequest(
            #         id=tc['id'],
            #         spec=self._process_options().tools_by_name[tc['function']['name']],
            #         args=json.loads(tc['function']['arguments'] or '{}'),
            #         raw_args=tc['function']['arguments'],
            #     )
            #     for tc in message_or_delta.get('tool_calls', [])
            # ] or None,
        )
