"""
Translation passes between the mc chat IR and the anthropic Messages API IR (`ommlds/backends/anthropic/protocol`).

Anthropic is a genuinely distinct API (not an openai-compat dialect): a typed sse *event family* assembled by a small
state machine, system prompt hoisted out of the message list, content as typed blocks. The shared machinery it rides
is only the http/sse transport (`minichain/http/stream.py`) and the service skeleton - not the wire format.
"""
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats.json import all as json

from ....backends.anthropic.protocol import types as pt
from ....backends.anthropic.protocol.sse.events import AnthropicSseDecoderEvents
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.types import AiChoice
from ...chat.messages import AiMessage
from ...chat.messages import AnyAiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import ToolUseMessage
from ...chat.messages import ToolUseResultMessage
from ...chat.messages import UserMessage
from ...chat.stream.types import AiDelta
from ...chat.stream.types import ContentAiDelta
from ...chat.stream.types import PartialToolUseAiDelta
from ...chat.tools.types import Tool
from ...content.render.standard import render_content_str
from ...llms.stopreasons import EndTurnStopReason
from ...llms.stopreasons import MaxTokensStopReason
from ...llms.stopreasons import OtherStopReason
from ...llms.stopreasons import StopReason
from ...llms.stopreasons import StopSequenceStopReason
from ...llms.stopreasons import ToolUseStopReason
from ...llms.types import StopReasonOutput
from ...llms.types import TokenUsage
from ...llms.types import TokenUsageOutput
from ...tools.jsonschema import build_tool_spec_params_json_schema
from ...tools.types import ToolUse


##
# Requests


def get_ant_message_content(m: Message) -> str | None:
    if isinstance(m, AiMessage):
        return check.isinstance(m.c, str)

    elif isinstance(m, (UserMessage, SystemMessage)):
        return check.isinstance(m.c, str)

    else:
        raise TypeError(m)


class BuiltAntMessages(ta.NamedTuple):
    messages: list[pt.Message]
    system: list[pt.Content] | None


ROLES_MAP: ta.Mapping[type[Message], str] = {
    SystemMessage: 'system',
    UserMessage: 'user',
    AiMessage: 'assistant',
    ToolUseMessage: 'assistant',
}


def build_ant_request_messages(msgs: ta.Iterable[Message]) -> BuiltAntMessages:
    messages: list[pt.Message] = []
    system: list[pt.Content] | None = None

    for i, m in enumerate(msgs):
        if isinstance(m, SystemMessage):
            if i or system is not None:
                raise Exception('Only supports one system message and must be first')
            system = [pt.Text(check.not_none(get_ant_message_content(m)))]

        elif isinstance(m, ToolUseResultMessage):
            messages.append(pt.Message(
                role='user',
                content=[pt.ToolResult(
                    tool_use_id=check.not_none(m.tur.id),
                    content=json.dumps_compact(msh.marshal(m.tur.c)) if not isinstance(m.tur.c, str) else m.tur.c,
                )],
            ))

        elif isinstance(m, AiMessage):
            messages.append(pt.Message(
                role='assistant',
                content=[
                    *([pt.Text(check.isinstance(m.c, str))] if m.c is not None else []),
                ],
            ))

        elif isinstance(m, ToolUseMessage):
            messages.append(pt.Message(
                role='assistant',
                content=[
                    pt.ToolUse(
                        id=check.not_none(m.tu.id),
                        name=check.not_none(m.tu.name),
                        input=m.tu.args,
                    ),
                ],
            ))

        else:
            messages.append(pt.Message(
                role=ROLES_MAP[type(m)],  # type: ignore[arg-type]
                content=[pt.Text(check.isinstance(get_ant_message_content(m), str))],
            ))

    return BuiltAntMessages(messages, system)


def build_ant_request_tool(t: Tool) -> pt.ToolSpec:
    return pt.ToolSpec(
        name=check.not_none(t.spec.name),
        description=render_content_str(t.spec.desc) if t.spec.desc is not None else '',
        input_schema=build_tool_spec_params_json_schema(t.spec),
    )


##
# Responses


def build_mc_stop_reason(stop_reason: str | None) -> StopReason | None:
    if stop_reason is None:
        return None
    elif stop_reason == 'end_turn':
        return EndTurnStopReason()
    elif stop_reason == 'max_tokens':
        return MaxTokensStopReason()
    elif stop_reason == 'tool_use':
        return ToolUseStopReason()
    elif stop_reason == 'stop_sequence':
        return StopSequenceStopReason()
    else:
        return OtherStopReason(stop_reason)


def build_mc_choices_response(msg: pt.Message) -> ChatChoicesResponse:
    out: list[AnyAiMessage] = []

    content = msg.content
    if isinstance(content, str):
        out.append(AiMessage(content))
    elif content is not None:
        for c in content:
            if isinstance(c, pt.Text):
                out.append(AiMessage(c.text))
            elif isinstance(c, pt.ToolUse):
                out.append(ToolUseMessage(ToolUse(
                    id=c.id,
                    name=c.name,
                    args=dict(c.input),
                )))
            else:
                raise TypeError(c)

    return ChatChoicesResponse(
        [AiChoice(out)],

        tv.collect(
            *([TokenUsageOutput(TokenUsage(
                input=u.input_tokens or 0,
                output=u.output_tokens or 0,
                total=(u.input_tokens or 0) + (u.output_tokens or 0),
            ))] if (u := msg.usage) is not None else []),

            *([StopReasonOutput(sr)] if (sr := build_mc_stop_reason(msg.stop_reason)) is not None else []),
        ),
    )


##
# Streaming


class AnthropicSseDeltaTranslator(lang.Final):
    """
    The anthropic streaming state machine, extracted from the old inline `invoke`. Anthropic frames a response as a
    typed event sequence - message_start, then per content block a (content_block_start, content_block_delta*,
    content_block_stop), then message_delta + message_stop - and the deltas reference their block by `index`, which the
    standard joiner uses for grouping. This holds the envelope/ordering invariants the protocol guarantees.
    """

    def __init__(self) -> None:
        super().__init__()

        self._msg_start: AnthropicSseDecoderEvents.MessageStart | None = None
        self._cbk_start: AnthropicSseDecoderEvents.ContentBlockStart | None = None
        self._msg_stop: AnthropicSseDecoderEvents.MessageStop | None = None

    class Result(ta.NamedTuple):
        deltas: ta.Sequence[AiDelta]
        done: bool = False

    def translate(self, ev: AnthropicSseDecoderEvents.Event) -> AnthropicSseDeltaTranslator.Result:
        Events = AnthropicSseDecoderEvents  # noqa

        if isinstance(ev, Events.MessageStart):
            check.none(self._msg_start)
            self._msg_start = ev
            if ev.message.content:
                raise NotImplementedError
            return self.Result([])

        elif isinstance(ev, Events.ContentBlockStart):
            check.not_none(self._msg_start)
            check.none(self._cbk_start)
            self._cbk_start = ev

            cb = ev.content_block
            if isinstance(cb, Events.ContentBlockStart.Text):
                return self.Result([ContentAiDelta(cb.text)])
            elif isinstance(cb, Events.ContentBlockStart.ToolUse):
                return self.Result([PartialToolUseAiDelta(
                    id=cb.id,
                    name=cb.name,
                    index=ev.index,
                    raw_args=cb.input,
                )])
            else:
                raise TypeError(cb)

        elif isinstance(ev, Events.ContentBlockDelta):
            check.not_none(self._cbk_start)

            d = ev.delta
            if isinstance(d, Events.ContentBlockDelta.TextDelta):
                return self.Result([ContentAiDelta(d.text)])
            elif isinstance(d, Events.ContentBlockDelta.InputJsonDelta):
                return self.Result([PartialToolUseAiDelta(
                    index=ev.index,
                    raw_args=d.partial_json,
                )])
            else:
                raise TypeError(d)

        elif isinstance(ev, Events.ContentBlockStop):
            check.not_none(self._cbk_start)
            self._cbk_start = None
            return self.Result([])

        elif isinstance(ev, Events.MessageDelta):
            check.not_none(self._msg_start)
            check.none(self._cbk_start)
            return self.Result([])

        elif isinstance(ev, Events.MessageStop):
            check.not_none(self._msg_start)
            check.none(self._msg_stop)
            self._msg_stop = ev
            return self.Result([], done=True)

        elif isinstance(ev, Events.Ping):
            return self.Result([])

        else:
            raise TypeError(ev)

    def finish(self) -> None:
        # The stream must have closed cleanly: a message_stop was seen and no content block was left open.
        check.not_none(self._msg_stop)
        check.none(self._cbk_start)
