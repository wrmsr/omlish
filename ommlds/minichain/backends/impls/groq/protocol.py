import itertools

from omlish import check
from omlish.formats import json

from .....backends.groq import protocol as pt
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.stream.types import AiChoiceDeltas
from ....chat.choices.types import AiChoice
from ....chat.messages import AiMessage
from ....chat.messages import AnyAiMessage
from ....chat.messages import Chat
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.stream.types import AiDelta
from ....chat.stream.types import ContentAiDelta
from ....chat.stream.types import ToolUseAiDelta
from ....chat.tools.types import Tool
from ....content.prepare import prepare_content_str
from ....tools.jsonschema import build_tool_spec_params_json_schema
from ....tools.types import ToolUse


##


def build_gq_request_messages(chat: Chat) -> list[pt.ChatCompletionRequest.Message]:
    gq_msgs: list[pt.ChatCompletionRequest.Message] = []

    for _, g in itertools.groupby(chat, lambda mc_m: isinstance(mc_m, AnyAiMessage)):
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
                gq_msgs.append(pt.ChatCompletionRequest.AssistantMessage(
                    content=check.isinstance(mc_ai_msg.c, str) if mc_ai_msg is not None else None,
                    tool_calls=[
                        pt.ChatCompletionRequest.AssistantMessage.ToolCall(
                            function=pt.ChatCompletionRequest.AssistantMessage.ToolCall.Function(
                                name=mc_tu_msg.tu.name,
                                arguments=check.not_none(mc_tu_msg.tu.raw_args),
                            ),
                            id=check.not_none(mc_tu_msg.tu.id),
                        )
                        for mc_tu_msg in mc_tu_msgs
                    ] if mc_tu_msgs else None,
                ))

        else:
            for mc_msg in mc_msgs:
                if isinstance(mc_msg, SystemMessage):
                    gq_msgs.append(pt.ChatCompletionRequest.SystemMessage(
                        content=check.isinstance(mc_msg.c, str),
                    ))

                elif isinstance(mc_msg, UserMessage):
                    gq_msgs.append(pt.ChatCompletionRequest.UserMessage(
                        content=check.isinstance(mc_msg.c, str),
                    ))

                elif isinstance(mc_msg, ToolUseResultMessage):
                    gq_msgs.append(pt.ChatCompletionRequest.ToolMessage(
                        tool_call_id=check.not_none(mc_msg.tur.id),
                        content=check.isinstance(mc_msg.tur.c, str),
                    ))

                else:
                    raise TypeError(mc_msg)

    return gq_msgs


def build_gq_request_tool(t: Tool) -> pt.ChatCompletionRequest.Tool:
    return pt.ChatCompletionRequest.Tool(
        function=pt.ChatCompletionRequest.Tool.Function(
            name=check.not_none(t.spec.name),
            description=prepare_content_str(t.spec.desc),
            parameters=build_tool_spec_params_json_schema(t.spec),
        ),
    )


def build_mc_choices_response(gq_resp: pt.ChatCompletionResponse) -> ChatChoicesResponse:
    def build_choice(gq_choice: pt.ChatCompletionResponse.Choice) -> AiChoice:
        gq_msg = gq_choice.message

        lst: list[AnyAiMessage] = []

        if gq_msg.content is not None:
            lst.append(AiMessage(
                check.isinstance(gq_msg.content, str),
            ))

        for gq_tc in gq_msg.tool_calls or []:
            lst.append(ToolUseMessage(ToolUse(
                id=gq_tc.id,
                name=gq_tc.function.name,
                args=json.loads(gq_tc.function.arguments or '{}'),
                raw_args=gq_tc.function.arguments,
            )))

        return AiChoice(lst)

    return ChatChoicesResponse(list(map(build_choice, gq_resp.choices)))


def build_mc_ai_choice_deltas(delta: pt.ChatCompletionChunk.Choice.Delta) -> AiChoiceDeltas:
    if delta.role in (None, 'assistant'):
        lst: list[AiDelta] = []

        if delta.content is not None:
            lst.append(ContentAiDelta(delta.content))

        for tc in delta.tool_calls or []:
            tc_fn = check.not_none(tc.function)
            lst.append(ToolUseAiDelta(
                id=tc.id,
                name=check.not_none(tc_fn.name),
                args=json.loads(tc_fn.arguments or '{}'),
            ))

        return AiChoiceDeltas(lst)

    elif delta.channel in ('analysis', 'commentary'):
        return AiChoiceDeltas([])

    else:
        raise ValueError(delta)
