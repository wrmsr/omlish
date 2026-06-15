"""
Translation passes between the mc chat IR and the openai Responses API IR (`ommlds/backends/openai/protocol/responses`)
- the modern, item-based openai api, distinct from (and alongside) the chat-completions dialect.
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv
from omlish.formats.json import all as json

from .....backends.openai.protocol import responses as pt
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.types import ChatChoice
from ....chat.messages import AiMessage
from ....chat.messages import AnyAiMessage
from ....chat.messages import Chat
from ....chat.messages import DeveloperMessage
from ....chat.messages import SystemMessage
from ....chat.messages import ThinkingMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.stream.types import AiDelta
from ....chat.stream.types import ContentAiDelta
from ....chat.stream.types import PartialToolUseAiDelta
from ....chat.stream.types import ThinkingAiDelta
from ....chat.tools.types import Tool
from ....content.render.standard import render_content_str
from ....llms.types import TokenUsage
from ....llms.types import TokenUsageOutput
from ....tools.jsonschema import build_tool_spec_params_json_schema
from ....tools.types import ToolUse


##
# Requests


def build_rsp_input_items(chat: Chat) -> list[pt.ResponsesInputItem]:
    items: list[pt.ResponsesInputItem] = []

    for m in chat:
        if isinstance(m, SystemMessage):
            items.append(pt.MessageResponsesInputItem(
                role='system',
                content=render_content_str(m.c),
            ))

        elif isinstance(m, DeveloperMessage):
            items.append(pt.MessageResponsesInputItem(
                role='developer',
                content=render_content_str(m.c),
            ))

        elif isinstance(m, UserMessage):
            items.append(pt.MessageResponsesInputItem(
                role='user',
                content=render_content_str(m.c),
            ))

        elif isinstance(m, AiMessage):
            items.append(pt.MessageResponsesInputItem(
                role='assistant',
                content=render_content_str(m.c) if m.c is not None else '',
            ))

        elif isinstance(m, ToolUseMessage):
            items.append(pt.FunctionCallResponsesInputItem(
                call_id=check.not_none(m.tu.id),
                name=m.tu.name,
                arguments=m.tu.raw_args if m.tu.raw_args is not None else json.dumps_compact(dict(m.tu.args)),
            ))

        elif isinstance(m, ToolUseResultMessage):
            items.append(pt.FunctionCallOutputResponsesInputItem(
                call_id=check.not_none(m.tur.id),
                output=render_content_str(m.tur.c),
            ))

        elif isinstance(m, ThinkingMessage):
            # Thinking is not (currently) round-tripped to the api.
            continue

        else:
            raise TypeError(m)

    return items


def build_rsp_request_tool(t: Tool) -> pt.FunctionResponsesTool:
    return pt.FunctionResponsesTool(
        name=check.not_none(t.spec.name),
        description=render_content_str(t.spec.desc) if t.spec.desc is not None else None,
        parameters=build_tool_spec_params_json_schema(t.spec),
    )


##
# Responses


def build_mc_messages_from_output_item(item: pt.ResponsesOutputItem) -> list[AnyAiMessage]:
    if isinstance(item, pt.ReasoningResponsesOutputItem):
        if (st := '\n\n'.join(s.text for s in item.summary)):
            return [ThinkingMessage(st)]
        return []

    elif isinstance(item, pt.MessageResponsesOutputItem):
        texts: list[str] = []
        for part in item.content:
            if isinstance(part, pt.OutputTextResponsesOutputContentPart):
                texts.append(part.text)
            elif isinstance(part, pt.RefusalResponsesOutputContentPart):
                texts.append(part.refusal)
            else:
                raise TypeError(part)
        return [AiMessage(''.join(texts))]

    elif isinstance(item, pt.FunctionCallResponsesOutputItem):
        return [ToolUseMessage(ToolUse(
            id=item.call_id,
            name=item.name,
            args=json.loads(item.arguments or '{}'),
            raw_args=item.arguments,
        ))]

    else:
        raise TypeError(item)


def build_mc_choices_response(rsp: pt.ResponsesResponse) -> ChatChoicesResponse:
    msgs: list[AnyAiMessage] = []
    for item in rsp.output:
        msgs.extend(build_mc_messages_from_output_item(item))

    return ChatChoicesResponse(
        [ChatChoice(msgs)],

        tv.collect(
            *([TokenUsageOutput(TokenUsage(
                input=u.input_tokens or 0,
                output=u.output_tokens or 0,
                total=u.total_tokens or 0,
            ))] if (u := rsp.usage) is not None else []),
        ),
    )


##
# Streaming


@dc.dataclass()
class OpenaiResponsesStreamError(Exception):
    event: pt.ResponsesSseEvents.Event


class ResponsesSseDeltaTranslator(lang.Final):
    """
    Incrementally translates Responses sse events into mc AiDeltas. Effectively stateless: function-call heads carry
    their ids/names on the `output_item.added` event and deltas carry their output indexes, so the standard
    uuid-stamping/joining machinery handles grouping without per-stream bookkeeping here.
    """

    class Result(ta.NamedTuple):
        deltas: ta.Sequence[AiDelta]
        done: bool = False

    def translate(self, ev: pt.ResponsesSseEvents.Event) -> ResponsesSseDeltaTranslator.Result:
        if isinstance(ev, pt.ResponsesSseEvents.OutputTextDelta):
            return self.Result([ContentAiDelta(ev.delta)])

        elif isinstance(ev, (
                pt.ResponsesSseEvents.ReasoningSummaryTextDelta,
                pt.ResponsesSseEvents.ReasoningTextDelta,
        )):
            return self.Result([ThinkingAiDelta(ev.delta)])

        elif isinstance(ev, pt.ResponsesSseEvents.OutputItemAdded):
            if isinstance(item := ev.item, pt.FunctionCallResponsesOutputItem):
                return self.Result([PartialToolUseAiDelta(
                    id=item.call_id,
                    name=item.name,
                    index=ev.output_index,
                    raw_args=item.arguments or None,
                )])
            return self.Result([])

        elif isinstance(ev, pt.ResponsesSseEvents.FunctionCallArgumentsDelta):
            return self.Result([PartialToolUseAiDelta(
                index=ev.output_index,
                raw_args=ev.delta,
            )])

        elif isinstance(ev, pt.ResponsesSseEvents.Completed):
            return self.Result([], done=True)

        elif isinstance(ev, (
                pt.ResponsesSseEvents.Failed,
                pt.ResponsesSseEvents.Incomplete,
                pt.ResponsesSseEvents.Error,
        )):
            raise OpenaiResponsesStreamError(ev)

        else:
            # Lifecycle / part-boundary / done-summary events carry no incremental information.
            return self.Result([])
