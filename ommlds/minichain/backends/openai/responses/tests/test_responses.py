# ruff: noqa: SLF001
"""
Offline coverage of the openai Responses backend: chat -> input-item translation, flat function tools, output-item ->
message translation with usage, and the streaming event -> delta translator driven through the real joiner - everything
short of the network (which the @online smoke covers).
"""
import json
import typing as ta

import pytest

from omlish import check
from omlish import marshal as msh
from omlish.http import sse

from ......backends.openai.protocol import responses as pt
from .....chat.messages import AiMessage
from .....chat.messages import SystemMessage
from .....chat.messages import ThinkingMessage
from .....chat.messages import ToolUseMessage
from .....chat.messages import ToolUseResultMessage
from .....chat.messages import UserMessage
from .....chat.stream.joining import AiDeltaJoiner
from .....chat.stream.types import ThinkingAiDelta
from .....chat.tools.types import Tool
from .....llms.types import MaxTokens
from .....llms.types import Temperature
from .....llms.types import TokenUsageOutput
from .....standard import ApiKey
from .....tools.types import ToolSpec
from .....tools.types import ToolUse
from .....tools.types import ToolUseResult
from ..chat import OpenaiResponsesChatChoicesService
from ..protocol import OpenaiResponsesStreamError
from ..protocol import ResponsesSseDeltaTranslator
from ..protocol import build_mc_choices_response
from ..protocol import build_rsp_input_items
from ..protocol import build_rsp_request_tool
from ..stream import OpenaiResponsesChatChoicesStreamService


##


def test_build_input_items():
    items = build_rsp_input_items([
        SystemMessage('be nice'),
        UserMessage('weather in tokyo?'),
        ToolUseMessage(ToolUse(id='call_1', name='weather', args={'location': 'Tokyo'}, raw_args='{"location": "Tokyo"}')),  # noqa: E501
        ToolUseResultMessage(ToolUseResult(id='call_1', name='weather', c='sunny')),
        AiMessage('it is sunny'),
    ])

    assert [type(i) for i in items] == [
        pt.MessageResponsesInputItem,
        pt.MessageResponsesInputItem,
        pt.FunctionCallResponsesInputItem,
        pt.FunctionCallOutputResponsesInputItem,
        pt.MessageResponsesInputItem,
    ]

    sys_item = check.isinstance(items[0], pt.MessageResponsesInputItem)
    assert sys_item.role == 'system'
    assert sys_item.content == 'be nice'

    fc = check.isinstance(items[2], pt.FunctionCallResponsesInputItem)
    assert fc.call_id == 'call_1'
    assert fc.name == 'weather'
    assert json.loads(fc.arguments) == {'location': 'Tokyo'}

    fco = check.isinstance(items[3], pt.FunctionCallOutputResponsesInputItem)
    assert fco.call_id == 'call_1'
    assert fco.output == 'sunny'

    ai = check.isinstance(items[4], pt.MessageResponsesInputItem)
    assert ai.role == 'assistant'
    assert ai.content == 'it is sunny'


def test_build_request_tool():
    t = build_rsp_request_tool(Tool(ToolSpec(
        'weather',
        desc='get the weather',
    )))

    # Responses function tools are flat - name at the top level, not nested under a 'function' key.
    assert t.name == 'weather'
    assert t.description == 'get the weather'
    assert t.parameters is not None


def test_request_honors_options():
    svc = OpenaiResponsesChatChoicesService(ApiKey('k'))

    req = svc._build_rsp_request(
        # ChatChoicesRequest-alike: anything with `.v` (the chat) and `.options`.
        _Req([UserMessage('hi')], [Temperature(.25), MaxTokens(123)]),
    )

    assert req.temperature == .25
    assert req.max_output_tokens == 123
    assert req.stream is None
    assert check.isinstance(next(iter(req.input)), pt.MessageResponsesInputItem).content == 'hi'


class _Req(ta.NamedTuple):
    v: ta.Any
    options: ta.Any


##


def test_build_choices_response():
    rsp = pt.ResponsesResponse(
        id='resp_1',
        status='completed',
        output=[
            pt.ReasoningResponsesOutputItem(
                summary=[pt.ReasoningResponsesOutputItem.SummaryText(text='thinking')],
            ),
            pt.MessageResponsesOutputItem(
                content=[pt.OutputTextResponsesOutputContentPart(text='hello there')],
            ),
            pt.FunctionCallResponsesOutputItem(
                call_id='call_1',
                name='weather',
                arguments='{"location":"Tokyo"}',
            ),
        ],
        usage=pt.ResponsesUsage(input_tokens=11, output_tokens=22, total_tokens=33),
    )

    out = build_mc_choices_response(rsp)

    gen = check.single(out.v.gs)
    chat = gen.chat
    assert [type(m) for m in chat] == [ThinkingMessage, AiMessage, ToolUseMessage]
    assert check.isinstance(chat[0], ThinkingMessage).c == 'thinking'
    assert check.isinstance(chat[1], AiMessage).c == 'hello there'
    tu = check.isinstance(chat[2], ToolUseMessage).tu
    assert tu.id == 'call_1'
    assert tu.name == 'weather'
    assert tu.args == {'location': 'Tokyo'}

    tuo = check.not_none(gen.outputs.get(TokenUsageOutput))
    assert tuo.v.input == 11
    assert tuo.v.output == 22
    assert tuo.v.total == 33


##


def _event(type_: str, **kwargs: ta.Any) -> pt.ResponsesSseEvents.Event:
    return msh.unmarshal({'type': type_, **kwargs}, pt.ResponsesSseEvents.Event)


def test_stream_translate_and_join():
    rsp_stub = {'id': 'resp_1', 'object': 'response'}

    events = [
        _event('response.created', response=rsp_stub),
        _event('response.output_text.delta', item_id='m', output_index=0, content_index=0, delta='hel'),
        _event('response.output_text.delta', item_id='m', output_index=0, content_index=0, delta='lo there'),
        _event(
            'response.output_item.added',
            output_index=1,
            item={'type': 'function_call', 'call_id': 'call_1', 'name': 'weather', 'arguments': ''},
        ),
        _event('response.function_call_arguments.delta', item_id='f', output_index=1, delta='{"location":'),
        _event('response.function_call_arguments.delta', item_id='f', output_index=1, delta='"Tokyo"}'),
        _event('response.completed', response=rsp_stub),
    ]

    translator = ResponsesSseDeltaTranslator()
    joiner = AiDeltaJoiner()
    done = False
    for ev in events:
        res = translator.translate(ev)
        if res.deltas:
            joiner.add(res.deltas)
        if res.done:
            done = True

    assert done

    joined = joiner.build()
    assert [type(m) for m in joined] == [AiMessage, ToolUseMessage]
    assert check.isinstance(joined[0], AiMessage).c == 'hello there'
    tu = check.isinstance(joined[1], ToolUseMessage).tu
    assert tu.id == 'call_1'
    assert tu.name == 'weather'
    assert tu.args == {'location': 'Tokyo'}


def test_translate_reasoning():
    translator = ResponsesSseDeltaTranslator()

    res = translator.translate(_event(
        'response.reasoning_text.delta',
        item_id='r', output_index=0, content_index=0, delta='hmm',
    ))
    (d,) = res.deltas
    assert check.isinstance(d, ThinkingAiDelta).c == 'hmm'
    assert not res.done

    # Lifecycle / boundary events carry no incremental content.
    res2 = translator.translate(_event('response.in_progress', response={'id': 'r', 'object': 'response'}))
    assert not res2.deltas
    assert not res2.done


def test_translate_error_raises():
    translator = ResponsesSseDeltaTranslator()
    with pytest.raises(OpenaiResponsesStreamError):
        translator.translate(_event('error', message='boom'))


##


@pytest.mark.asyncs('asyncio')
async def test_stream_process_sse():
    svc = OpenaiResponsesChatChoicesStreamService(ApiKey('k'))

    def _sse(ev: pt.ResponsesSseEvents.Event) -> sse.SseEvent:
        # Marshal against the polymorphic base so the 'type' tag is emitted (as the real wire data carries it).
        raw = msh.marshal(ev, pt.ResponsesSseEvents.Event)
        return sse.SseEvent(b'message', json.dumps(raw).encode('utf-8'))

    out = await svc._process_sse(
        ResponsesSseDeltaTranslator(),
        _sse(_event('response.output_text.delta', item_id='m', output_index=0, content_index=0, delta='hi')),
    )
    (deltas,) = out
    assert deltas is not None

    # The completed event flushes a None terminator.
    out2 = await svc._process_sse(
        ResponsesSseDeltaTranslator(),
        _sse(_event('response.completed', response={'id': 'r', 'object': 'response'})),
    )
    assert out2[-1] is None

    # Non-event sse outputs are ignored.
    assert await svc._process_sse(ResponsesSseDeltaTranslator(), sse.SseComment(b'hi')) == []


##


def test_marshal_round_trips():
    req = pt.ResponsesRequest(
        model='gpt-5',
        input=build_rsp_input_items([UserMessage('hi')]),
        tools=[build_rsp_request_tool(Tool(ToolSpec('weather')))],
        temperature=.5,
        stream=True,
    )
    # Compare via marshal stability (unmarshal normalizes Sequences to tuples, so == on the dataclasses is noisy).
    m = msh.marshal(req)
    assert msh.marshal(msh.unmarshal(m, pt.ResponsesRequest)) == m

    ev = _event('response.output_text.delta', item_id='m', output_index=0, content_index=0, delta='x')
    raw = check.isinstance(msh.marshal(ev, pt.ResponsesSseEvents.Event), dict)
    assert raw['type'] == 'response.output_text.delta'
    assert msh.unmarshal(raw, pt.ResponsesSseEvents.Event) == ev
