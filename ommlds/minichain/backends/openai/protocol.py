import itertools
import typing as ta

from omlish import cached
from omlish import check
from omlish import typedvalues as tv
from omlish.formats.json import all as json

from ....backends.openai import protocol as pt
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.types import ChatChoices
from ...chat.choices.types import ChatChoicesOptions
from ...chat.generations import ChatGeneration
from ...chat.messages import AiMessage
from ...chat.messages import AnyAiMessage
from ...chat.messages import Chat
from ...chat.messages import SystemMessage
from ...chat.messages import ToolUseMessage
from ...chat.messages import ToolUseResultMessage
from ...chat.messages import UserMessage
from ...chat.stream.types import AiDeltas
from ...chat.stream.types import ContentAiDelta
from ...chat.stream.types import PartialToolUseAiDelta
from ...chat.tools.types import Tool
from ...content.json import JsonContent
from ...content.render.standard import render_content_str
from ...llms.stopreasons import ContentFilterStopReason
from ...llms.stopreasons import EndTurnStopReason
from ...llms.stopreasons import MaxTokensStopReason
from ...llms.stopreasons import OtherStopReason
from ...llms.stopreasons import StopReason
from ...llms.stopreasons import ToolUseStopReason
from ...llms.types import MaxCompletionTokens
from ...llms.types import MaxTokens
from ...llms.types import StopReasonOutput
from ...llms.types import Temperature
from ...llms.types import TokenUsage
from ...llms.types import TokenUsageOutput
from ...tools.jsonschema import build_tool_spec_params_json_schema
from ...tools.types import ToolSpec
from ...tools.types import ToolUse
from ...types import Option


##


def build_oai_request_msgs(mc_chat: Chat) -> ta.Sequence[pt.ChatCompletionMessage]:
    oai_msgs: list[pt.ChatCompletionMessage] = []

    for _, g in itertools.groupby(mc_chat, lambda mc_m: isinstance(mc_m, AnyAiMessage)):
        mc_msgs = list(g)

        if isinstance(mc_msgs[0], AnyAiMessage):
            tups: list[tuple[AiMessage | None, list[ToolUseMessage]]] = []
            for mc_msg in mc_msgs:
                if isinstance(mc_msg, AiMessage):
                    tups.append((mc_msg, []))

                elif isinstance(mc_msg, ToolUseMessage):
                    if not tups:
                        tups.append((None, []))
                    tups[-1][1].append(mc_msg)

                else:
                    raise TypeError(mc_msg)

            for mc_ai_msg, mc_tu_msgs in tups:
                oai_msgs.append(pt.AssistantChatCompletionMessage(
                    content=check.isinstance(mc_ai_msg.c, (str, None)) if mc_ai_msg is not None else None,
                    tool_calls=[
                        pt.AssistantChatCompletionMessage.ToolCall(
                            id=check.not_none(mc_tu_msg.tu.id),
                            function=pt.AssistantChatCompletionMessage.ToolCall.Function(
                                arguments=check.not_none(mc_tu_msg.tu.raw_args),
                                name=mc_tu_msg.tu.name,
                            ),
                        )
                        for mc_tu_msg in mc_tu_msgs
                    ] if mc_tu_msgs else None,
                ))

        else:
            for mc_msg in mc_msgs:
                if isinstance(mc_msg, SystemMessage):
                    oai_msgs.append(pt.SystemChatCompletionMessage(
                        content=check.isinstance(mc_msg.c, str),
                    ))

                elif isinstance(mc_msg, UserMessage):
                    oai_msgs.append(pt.UserChatCompletionMessage(
                        content=render_content_str(mc_msg.c),
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


def build_mc_ai_choice(oai_choice: pt.ChatCompletionResponseChoice) -> ChatGeneration:
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

    return ChatGeneration(
        cur,

        tv.collect(
            *build_mc_stop_reason_output_(oai_choice.finish_reason),
        ),
    )


def build_mc_token_usage(tu: pt.CompletionUsage) -> TokenUsage:
    return TokenUsage(
        input=tu.prompt_tokens,
        output=tu.completion_tokens,
        total=tu.total_tokens,
    )


def build_mc_token_usage_output_(tu: pt.CompletionUsage | None) -> ta.Sequence[TokenUsageOutput]:
    return [TokenUsageOutput(build_mc_token_usage(tu))] if tu is not None else []


def build_mc_ai_choices(oai_resp: pt.ChatCompletionResponse) -> ChatChoices:
    return ChatChoices(
        [
            build_mc_ai_choice(oai_choice)
            for oai_choice in oai_resp.choices
        ],

        tv.collect(
            *build_mc_token_usage_output_(oai_resp.usage),
        ),
    )


def build_mc_stop_reason(finish_reason: str) -> StopReason:
    # openai-compat chat-completions finish reasons.
    if finish_reason == 'stop':
        return EndTurnStopReason()
    elif finish_reason == 'length':
        return MaxTokensStopReason()
    elif finish_reason in ('tool_calls', 'function_call'):
        return ToolUseStopReason()
    elif finish_reason == 'content_filter':
        return ContentFilterStopReason()
    else:
        return OtherStopReason(finish_reason)


def build_mc_stop_reason_output_(finish_reason: str | None) -> ta.Sequence[StopReasonOutput]:
    return [StopReasonOutput(build_mc_stop_reason(finish_reason))] if finish_reason is not None else []


def build_mc_choices_response(oai_resp: pt.ChatCompletionResponse) -> ChatChoicesResponse:
    return ChatChoicesResponse(
        build_mc_ai_choices(oai_resp),
    )


def build_mc_ai_deltas(delta: pt.ChatCompletionChunkChoiceDelta) -> AiDeltas:
    # openai-compat dialect (groq/cerebras gpt-oss): reasoning-channel deltas are not (currently) surfaced.
    if delta.channel in ('analysis', 'commentary'):
        return []

    if delta.content is not None:
        check.state(not delta.tool_calls)
        return [ContentAiDelta(delta.content)]

    elif delta.tool_calls is not None:
        check.state(delta.content is None)
        tc = check.single(delta.tool_calls)
        tc_fn = check.not_none(tc.function)
        return [PartialToolUseAiDelta(
            id=tc.id,
            name=tc_fn.name,
            index=tc.index,
            raw_args=tc_fn.arguments,
        )]

    else:
        return []


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
        max_completion_tokens=MaxCompletionTokens,
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

        with tv.consume(*self._options) as oc:
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
                    description=render_content_str(ts.desc) if ts.desc is not None else None,
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
            parallel_tool_calls=True if tools else None,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            **po.kwargs,
        )
