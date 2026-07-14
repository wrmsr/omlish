"""
Translation passes between the mc chat IR and the google generativelanguage (gemini) API IR
(`ommlds/backends/google/protocol`).

Google is a genuinely distinct API (not an openai-compat dialect): `contents` of typed `parts`, a hoisted
`system_instruction`, function-call/response parts, thought signatures. Only the http/sse transport is shared.
"""
import typing as ta

from omcore import check
from omcore import typedvalues as tv
from omcore.formats.json import all as json

from ....backends.google.protocol import types as pt
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.types import ChatChoices
from ...chat.generations import ChatGeneration
from ...chat.messages import AiMessage
from ...chat.messages import AnyAiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import ToolUseMessage
from ...chat.messages import ToolUseResultMessage
from ...chat.messages import UserMessage
from ...chat.metadata import ThoughtSignature
from ...chat.stream.choices.types import AiChoiceDeltas
from ...chat.stream.choices.types import AiChoicesDeltas
from ...chat.stream.types import AiDelta
from ...chat.stream.types import ContentAiDelta
from ...chat.stream.types import ToolUseAiDelta
from ...chat.tools.types import Tool
from ...content.json import JsonContent
from ...llms.stopreasons import ContentFilterStopReason
from ...llms.stopreasons import EndTurnStopReason
from ...llms.stopreasons import MaxTokensStopReason
from ...llms.stopreasons import OtherStopReason
from ...llms.stopreasons import StopReason
from ...llms.types import ModelNameOutput
from ...llms.types import StopReasonOutput
from ...tools.types import ToolUse
from .tools import build_tool_spec_schema


##
# Requests


ROLES_MAP: ta.Mapping[type[Message], pt.ContentRole | None] = {  # noqa
    SystemMessage: None,
    UserMessage: 'user',
    AiMessage: 'model',
    ToolUseMessage: 'model',
}


def make_str_content(
        s: str | None,
        *,
        role: pt.ContentRole | None = None,
) -> pt.Content | None:
    if s is None:
        return None

    return pt.Content(
        parts=[pt.Part(
            text=check.not_none(s),
        )],
        role=role,
    )


def build_g_request_content(m: Message) -> pt.Content:
    if isinstance(m, (AiMessage, SystemMessage, UserMessage)):
        return check.not_none(make_str_content(
            check.isinstance(m.c, str),
            role=ROLES_MAP[type(m)],
        ))

    elif isinstance(m, ToolUseResultMessage):
        tr_resp_val: pt.Value
        if m.tur.c is None:
            tr_resp_val = pt.NullValue()  # type: ignore[unreachable]
        elif isinstance(m.tur.c, str):
            tr_resp_val = pt.StringValue(m.tur.c)
        elif isinstance(m.tur.c, JsonContent):
            tr_resp_val = pt.StringValue(json.dumps_compact(m.tur.c))
        else:
            raise TypeError(m.tur.c)

        return pt.Content(
            parts=[pt.Part(
                function_response=pt.FunctionResponse(
                    id=m.tur.id,
                    name=m.tur.name,
                    response={
                        'value': tr_resp_val,
                    },
                ),
            )],
        )

    elif isinstance(m, ToolUseMessage):
        return pt.Content(
            parts=[pt.Part(
                function_call=pt.FunctionCall(
                    id=m.tu.id,
                    name=m.tu.name,
                    args=m.tu.args,
                ),
                **(
                    dict(thought_signature=ts_md.v)  # type: ignore
                    if (ts_md := m.metadata.get(ThoughtSignature)) is not None else {}
                ),
            )],
            role='model',
        )

    else:
        raise TypeError(m)


def pop_g_system_instruction(msgs: list[Message]) -> pt.Content | None:
    if not msgs:
        return None

    if not isinstance(m0 := msgs[0], SystemMessage):
        return None

    msgs.pop(0)
    return build_g_request_content(m0)


def build_g_request_tool(t: Tool) -> pt.Tool:
    return pt.Tool(
        function_declarations=[build_tool_spec_schema(t.spec)],
    )


##
# Responses


def _build_mc_part_message(part: pt.Part) -> AnyAiMessage:
    if (txt := part.text) is not None:
        return AiMessage(txt)
    elif (fc := part.function_call) is not None:
        return ToolUseMessage(ToolUse(
            id=fc.id,
            name=fc.name,
            args=fc.args or {},
        ))
    else:
        raise TypeError(part)


def build_mc_stop_reason(finish_reason: str | None) -> StopReason | None:
    # Google reports 'STOP' even on tool-calling turns; the driver's structural override corrects that.
    if finish_reason is None or finish_reason in ('FINISH_REASON_UNSPECIFIED', 'STOP'):
        return EndTurnStopReason() if finish_reason == 'STOP' else None
    elif finish_reason == 'MAX_TOKENS':
        return MaxTokensStopReason()
    elif finish_reason in ('SAFETY', 'RECITATION', 'BLOCKLIST', 'PROHIBITED_CONTENT', 'SPII'):
        return ContentFilterStopReason()
    else:
        return OtherStopReason(finish_reason)


def build_mc_choices_response(resp: pt.GenerateContentResponse) -> ChatChoicesResponse:
    ai_choices: list[ChatGeneration] = []
    for c in resp.candidates or []:
        out: list[AnyAiMessage] = []
        for part in check.not_none(check.not_none(c.content).parts):
            out.append(_build_mc_part_message(part))

        ai_choices.append(ChatGeneration(
            out,

            tv.collect(
                *(
                    [StopReasonOutput(sr)]
                    if (fr := c.finish_reason) is not None and (sr := build_mc_stop_reason(fr)) is not None
                    else []
                ),

                *([ModelNameOutput(resp.model_version)] if resp.model_version else []),
            ),
        ))

    return ChatChoicesResponse(
        ChatChoices(ai_choices),
    )


##
# Streaming


def build_mc_part_ai_delta(part: pt.Part) -> AiDelta | None:
    ai_delta: AiDelta

    if (txt := part.text) is not None:
        check.none(part.function_call)
        s = check.not_none(txt)
        if not s:
            return None
        ai_delta = ContentAiDelta(s)

    elif (fc := part.function_call) is not None:
        check.none(part.text)
        ai_delta = ToolUseAiDelta(
            id=fc.id,
            name=fc.name,
            args=fc.args,
        )

    else:
        raise ValueError(part)

    if part.thought_signature is not None:
        ai_delta = ai_delta.with_metadata(ThoughtSignature(part.thought_signature))

    return ai_delta


def build_mc_ai_choices_deltas(resp: pt.GenerateContentResponse) -> list[AiChoicesDeltas]:
    cnd = check.single(check.not_none(resp.candidates))

    return [
        AiChoicesDeltas([
            AiChoiceDeltas(
                [ap] if (ap := build_mc_part_ai_delta(part)) is not None else [],
            ),
        ])
        for part in check.not_none(cnd.content).parts or []
    ]
