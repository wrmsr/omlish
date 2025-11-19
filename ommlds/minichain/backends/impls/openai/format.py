import typing as ta

from omlish import cached
from omlish import check
from omlish import typedvalues as tv
from omlish.formats import json

from .....backends.openai import protocol as pt
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.types import AiChoice
from ....chat.choices.types import AiChoices
from ....chat.choices.types import ChatChoicesOptions
from ....chat.messages import AiMessage
from ....chat.messages import AnyAiMessage
from ....chat.messages import Chat
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.stream.types import AiDelta
from ....chat.stream.types import ContentAiDelta
from ....chat.stream.types import PartialToolUseAiDelta
from ....chat.tools.types import Tool
from ....content.json import JsonContent
from ....content.prepare import prepare_content_str
from ....llms.types import MaxTokens
from ....llms.types import Temperature
from ....llms.types import TokenUsage
from ....llms.types import TokenUsageOutput
from ....tools.jsonschema import build_tool_spec_params_json_schema
from ....tools.types import ToolSpec
from ....tools.types import ToolUse
from ....types import Option


##


def build_oai_request_msgs(mc_chat: Chat) -> ta.Sequence[pt.ChatCompletionMessage]:
    oai_msgs: list[pt.ChatCompletionMessage] = []

    for mc_msg in mc_chat:
        if isinstance(mc_msg, SystemMessage):
            oai_msgs.append(pt.SystemChatCompletionMessage(
                content=check.isinstance(mc_msg.c, str),
            ))

        elif isinstance(mc_msg, AiMessage):
            oai_msgs.append(pt.AssistantChatCompletionMessage(
                content=check.isinstance(mc_msg.c, (str, None)),
            ))

        elif isinstance(mc_msg, ToolUseMessage):
            oai_msgs.append(pt.AssistantChatCompletionMessage(
                tool_calls=[pt.AssistantChatCompletionMessage.ToolCall(
                    id=check.not_none(mc_msg.tu.id),
                    function=pt.AssistantChatCompletionMessage.ToolCall.Function(
                        arguments=check.not_none(mc_msg.tu.raw_args),
                        name=mc_msg.tu.name,
                    ),
                )],
            ))

        elif isinstance(mc_msg, UserMessage):
            oai_msgs.append(pt.UserChatCompletionMessage(
                content=prepare_content_str(mc_msg.c),
            ))

        elif isinstance(mc_msg, ToolUseResultMessage):
            tc: str
            if isinstance(mc_msg.tur.c, str):
                tc = mc_msg.tur.c
            elif isinstance(mc_msg.tur.c, JsonContent):
                tc = json.dumps_compact(mc_msg.tur.c)
            else:
                raise TypeError(mc_msg.tur.c)
            oai_msgs.append(pt.ToolChatCompletionMessage(
                tool_call_id=check.not_none(mc_msg.tur.id),
                content=tc,
            ))

        else:
            raise TypeError(mc_msg)

    return oai_msgs


#


def build_mc_ai_choice(oai_choice: pt.ChatCompletionResponseChoice) -> AiChoice:
    cur: list[AnyAiMessage] = []

    oai_msg = oai_choice.message

    if (oai_c := oai_msg.content) is not None:
        cur.append(AiMessage(check.isinstance(oai_c, str)))

    for oai_tc in oai_msg.tool_calls or []:
        cur.append(ToolUseMessage(ToolUse(
            id=oai_tc.id,
            name=oai_tc.function.name,
            args=json.loads(oai_tc.function.arguments or '{}'),
            raw_args=oai_tc.function.arguments,
        )))

    return AiChoice(cur)


def build_mc_ai_choices(oai_resp: pt.ChatCompletionResponse) -> AiChoices:
    return [
        build_mc_ai_choice(oai_choice)
        for oai_choice in oai_resp.choices
    ]


def build_mc_choices_response(oai_resp: pt.ChatCompletionResponse) -> ChatChoicesResponse:
    return ChatChoicesResponse(
        build_mc_ai_choices(oai_resp),

        tv.TypedValues(
            *([TokenUsageOutput(TokenUsage(
                input=tu.prompt_tokens,
                output=tu.completion_tokens,
                total=tu.total_tokens,
            ))] if (tu := oai_resp.usage) is not None else []),
        ),
    )


def build_mc_ai_delta(delta: pt.ChatCompletionChunkChoiceDelta) -> AiDelta:
    if delta.content is not None:
        check.state(not delta.tool_calls)
        return ContentAiDelta(delta.content)

    elif delta.tool_calls is not None:
        check.state(delta.content is None)
        tc = check.single(delta.tool_calls)
        tc_fn = check.not_none(tc.function)
        return PartialToolUseAiDelta(
            id=tc.id,
            name=tc_fn.name,
            raw_args=tc_fn.arguments,
        )

    else:
        raise ValueError(delta)


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

    DEFAULT_OPTIONS: ta.ClassVar[tv.TypedValues[Option]] = tv.TypedValues[Option](
        # Temperature(0.),
        # MaxTokens(1024),
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
            # temperature=0,
            # max_tokens=1024,
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
    def oai_request(self) -> pt.ChatCompletionRequest:
        po = self._process_options()

        tools: list[pt.ChatCompletionRequestTool] = [
            pt.ChatCompletionRequestTool(
                function=pt.ChatCompletionRequestTool.Function(
                    name=check.not_none(ts.name),
                    description=prepare_content_str(ts.desc),
                    parameters=build_tool_spec_params_json_schema(ts),
                ),
            )
            for ts in po.tools_by_name.values()
        ]

        return pt.ChatCompletionRequest(
            model=self._model,
            messages=build_oai_request_msgs(self._chat),
            top_p=1,
            tools=tools or None,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            **po.kwargs,
        )
