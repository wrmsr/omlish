import itertools

from omlish import check
from omlish import typedvalues as tv
from omlish.formats.json import all as json

from ....backends.ollama import protocol as pt
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.types import ChatChoices
from ...chat.generations import ChatGeneration
from ...chat.messages import AiMessage
from ...chat.messages import AnyAiMessage
from ...chat.messages import Chat
from ...chat.messages import SystemMessage
from ...chat.messages import ThinkingMessage
from ...chat.messages import ToolUseMessage
from ...chat.messages import ToolUseResultMessage
from ...chat.messages import UserMessage
from ...chat.stream.choices.types import AiChoiceDeltas
from ...chat.stream.types import AiDelta
from ...chat.stream.types import ContentAiDelta
from ...chat.stream.types import ThinkingAiDelta
from ...chat.stream.types import ToolUseAiDelta
from ...chat.tools.types import Tool
from ...content.json import JsonContent
from ...content.render.standard import render_content_str
from ...content.text import TextContent
from ...llms.stopreasons import EndTurnStopReason
from ...llms.stopreasons import MaxTokensStopReason
from ...llms.stopreasons import OtherStopReason
from ...llms.stopreasons import StopReason
from ...llms.types import ModelNameOutput
from ...llms.types import StopReasonOutput
from ...tools.jsonschema import build_tool_spec_params_json_schema
from ...tools.types import ToolUse


##


def build_ol_request_messages(chat: Chat) -> list[pt.Message]:
    ol_msgs: list[pt.Message] = []

    for _, g in itertools.groupby(chat, lambda mc_m: isinstance(mc_m, AnyAiMessage)):
        mc_msgs = list(g)

        if isinstance(mc_msgs[0], AnyAiMessage):
            tups: list[tuple[AiMessage | None, list[ToolUseMessage | ThinkingMessage]]] = []
            for mc_msg in mc_msgs:
                if isinstance(mc_msg, AiMessage):
                    tups.append((mc_msg, []))

                elif isinstance(mc_msg, (ToolUseMessage, ThinkingMessage)):
                    if not tups:
                        tups.append((None, []))
                    tups[-1][1].append(mc_msg)

                else:
                    raise TypeError(mc_msg)

            for mc_ai_msg, mc_tu_msgs in tups:
                tcs: list[pt.Message.ToolCall] = []
                ths: list[str] = []

                for tum in mc_tu_msgs or []:
                    if isinstance(tum, ToolUseMessage):
                        tcs.append(pt.Message.ToolCall(
                            function=pt.Message.ToolCall.Function(
                                name=tum.tu.name,
                                arguments=tum.tu.args,
                            ),
                            id=check.not_none(tum.tu.id),
                        ))

                    elif isinstance(tum, ThinkingMessage):
                        if (thc := tum.c.strip()):
                            ths.append(thc)

                    else:
                        raise TypeError(tum)

                ol_msgs.append(pt.Message(
                    role='assistant',
                    content=check.isinstance(mc_ai_msg.c, str) if mc_ai_msg is not None else None,
                    tool_calls=tcs or None,
                    thinking='\n\n'.join(ths) if ths else None,
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
                    # FIXME: generalized visitor lol
                    tur_c = mc_msg.tur.c
                    if isinstance(tur_c, str):
                        tur_cs = tur_c
                    elif isinstance(tur_c, TextContent):
                        tur_cs = tur_c.s
                    elif isinstance(tur_c, JsonContent):
                        tur_cs = json.dumps_compact(tur_c.v)
                    else:
                        raise TypeError(tur_c)

                    ol_msgs.append(pt.Message(
                        role='tool',
                        tool_name=mc_msg.tur.name,
                        content=tur_cs,
                    ))

                else:
                    raise TypeError(mc_msg)

    return ol_msgs


def build_ol_request_tool(t: Tool) -> pt.Tool:
    return pt.Tool(
        function=pt.Tool.Function(
            name=check.not_none(t.spec.name),
            description=render_content_str(t.spec.desc) if t.spec.desc is not None else None,
            parameters=build_tool_spec_params_json_schema(t.spec),
        ),
    )


def build_mc_choices_response(ol_resp: pt.ChatResponse) -> ChatChoicesResponse:
    ol_msg = ol_resp.message

    lst: list[AnyAiMessage] = []

    if ol_msg.role in (None, 'assistant'):
        if ol_msg.content:
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

    return ChatChoicesResponse(
        ChatChoices([
            ChatGeneration(
                lst,

                tv.collect(
                    *([StopReasonOutput(sr)] if (sr := build_mc_stop_reason(ol_resp.done_reason)) is not None else []),

                    *([ModelNameOutput(ol_resp.model)] if ol_resp.model else []),
                ),
            ),
        ]),

    )


def build_mc_stop_reason(done_reason: str | None) -> StopReason | None:
    # Ollama reports 'stop' even on tool-calling turns; the driver's structural override corrects that.
    if done_reason is None:
        return None
    elif done_reason == 'stop':
        return EndTurnStopReason()
    elif done_reason == 'length':
        return MaxTokensStopReason()
    else:
        return OtherStopReason(done_reason)


def build_mc_ai_choice_deltas(ol_resp: pt.ChatResponse) -> AiChoiceDeltas:
    ol_msg = ol_resp.message

    if ol_msg.role in (None, 'assistant'):
        lst: list[AiDelta] = []

        if ol_msg.content:
            lst.append(ContentAiDelta(ol_msg.content))

        if ol_msg.thinking:
            lst.append(ThinkingAiDelta(ol_msg.thinking))

        for tc in ol_msg.tool_calls or []:
            lst.append(ToolUseAiDelta(
                id=tc.id,
                name=check.not_none(tc.function.name),
                args=tc.function.arguments,
            ))

        return AiChoiceDeltas(lst)

    else:
        raise ValueError(ol_msg)
