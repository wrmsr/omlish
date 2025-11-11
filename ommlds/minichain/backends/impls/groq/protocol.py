from omlish import check
from omlish.formats import json

from .....backends.groq import protocol as pt
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.types import AiChoice
from ....chat.messages import AiMessage
from ....chat.messages import AnyAiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import UserMessage
from ....chat.stream.types import AiChoiceDeltas
from ....chat.stream.types import ContentAiChoiceDelta
from ....chat.tools.types import Tool
from ....content.prepare import prepare_content_str
from ....tools.jsonschema import build_tool_spec_params_json_schema
from ....tools.types import ToolUse


##


def build_gq_request_message(mc_msg: Message) -> pt.ChatCompletionRequest.Message:
    if isinstance(mc_msg, SystemMessage):
        return pt.ChatCompletionRequest.SystemMessage(
            content=check.isinstance(mc_msg.c, str),
        )

    elif isinstance(mc_msg, UserMessage):
        return pt.ChatCompletionRequest.UserMessage(
            content=check.isinstance(mc_msg.c, str),
        )

    elif isinstance(mc_msg, AiMessage):
        return pt.ChatCompletionRequest.AssistantMessage(
            content=check.isinstance(mc_msg.c, str),
        )

    elif isinstance(mc_msg, ToolUseMessage):
        raise NotImplementedError

    else:
        raise TypeError(mc_msg)


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
    if delta.role in (None, 'assistant') and delta.content is not None:
        return AiChoiceDeltas([ContentAiChoiceDelta(delta.content)])

    else:
        return AiChoiceDeltas([])
