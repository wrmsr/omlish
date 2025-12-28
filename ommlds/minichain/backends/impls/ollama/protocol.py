import itertools

from omlish import check

from .....backends.ollama import protocol as pt
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
from ....content.transform.prepare import prepare_content_str
from ....tools.jsonschema import build_tool_spec_params_json_schema
from ....tools.types import ToolUse


##


def build_ol_request_messages(chat: Chat) -> list[pt.Message]:
    ol_msgs: list[pt.Message] = []

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
                ol_msgs.append(pt.Message(
                    role='assistant',
                    content=check.isinstance(mc_ai_msg.c, str) if mc_ai_msg is not None else None,
                    tool_calls=[
                        pt.Message.ToolCall(
                            function=pt.Message.ToolCall.Function(
                                name=mc_tu_msg.tu.name,
                                arguments=mc_tu_msg.tu.args,
                            ),
                            id=check.not_none(mc_tu_msg.tu.id),
                        )
                        for mc_tu_msg in mc_tu_msgs
                    ] if mc_tu_msgs else None,
                ))

        else:
            for mc_msg in mc_msgs:
                if isinstance(mc_msg, SystemMessage):
                    ol_msgs.append(pt.Message(
                        role='system',
                        content=check.isinstance(mc_msg.c, str),
                    ))

                elif isinstance(mc_msg, UserMessage):
                    ol_msgs.append(pt.Message(
                        role='user',
                        content=check.isinstance(mc_msg.c, str),
                    ))

                elif isinstance(mc_msg, ToolUseResultMessage):
                    ol_msgs.append(pt.Message(
                        role='tool',
                        tool_name=mc_msg.tur.name,
                        content=check.isinstance(mc_msg.tur.c, str),
                    ))

                else:
                    raise TypeError(mc_msg)

    return ol_msgs


def build_ol_request_tool(t: Tool) -> pt.Tool:
    return pt.Tool(
        function=pt.Tool.Function(
            name=check.not_none(t.spec.name),
            description=prepare_content_str(t.spec.desc) if t.spec.desc is not None else None,
            parameters=build_tool_spec_params_json_schema(t.spec),
        ),
    )


def build_mc_choices_response(ol_resp: pt.ChatResponse) -> ChatChoicesResponse:
    ol_msg = ol_resp.message

    lst: list[AnyAiMessage] = []

    if ol_msg.role in (None, 'assistant'):
        if ol_msg.content is not None:
            lst.append(AiMessage(
                check.isinstance(ol_msg.content, str),
            ))

        for ol_tc in ol_msg.tool_calls or []:
            lst.append(ToolUseMessage(ToolUse(
                id=ol_tc.id,
                name=ol_tc.function.name,
                args=ol_tc.function.arguments,
            )))

    else:
        raise ValueError(ol_msg)

    return ChatChoicesResponse([AiChoice(lst)])


def build_mc_ai_choice_deltas(ol_resp: pt.ChatResponse) -> AiChoiceDeltas:
    ol_msg = ol_resp.message

    if ol_msg.role in (None, 'assistant'):
        lst: list[AiDelta] = []

        if ol_msg.content is not None:
            lst.append(ContentAiDelta(ol_msg.content))

        for tc in ol_msg.tool_calls or []:
            lst.append(ToolUseAiDelta(
                id=tc.id,
                name=check.not_none(tc.function.name),
                args=tc.function.arguments,
            ))

        return AiChoiceDeltas(lst)

    else:
        raise ValueError(ol_msg)
