import json
import typing as ta

import pytest

from omlish import marshal as msh

from ..events import ResponsesSseEvents
from ..request import FunctionCallOutputResponsesInputItem
from ..request import FunctionCallResponsesInputItem
from ..request import FunctionResponsesTool
from ..request import MessageResponsesInputItem
from ..request import ResponsesRequest
from ..response import FunctionCallResponsesOutputItem
from ..response import MessageResponsesOutputItem
from ..response import OutputTextResponsesOutputContentPart
from ..response import ReasoningResponsesOutputItem
from ..response import ResponsesResponse
from ..response import ResponsesUsage


def test_marshal_request_response():
    objs: list[tuple[type, ta.Any]] = [
        (ResponsesRequest, ResponsesRequest(
            model='gpt-5',
            input=(
                MessageResponsesInputItem(role='user', content='hi'),
                FunctionCallResponsesInputItem(call_id='call_1', name='weather', arguments='{"location":"Tokyo"}'),
                FunctionCallOutputResponsesInputItem(call_id='call_1', output='sunny'),
            ),
            tools=(FunctionResponsesTool(name='weather', parameters={'type': 'object'}),),
            temperature=.5,
            stream=True,
        )),
        (ResponsesResponse, ResponsesResponse(
            id='resp_1',
            status='completed',
            output=(
                ReasoningResponsesOutputItem(summary=(ReasoningResponsesOutputItem.SummaryText(text='hmm'),)),
                MessageResponsesOutputItem(content=(OutputTextResponsesOutputContentPart(text='hello'),)),
                FunctionCallResponsesOutputItem(call_id='call_1', name='weather', arguments='{}'),
            ),
            usage=ResponsesUsage(input_tokens=1, output_tokens=2, total_tokens=3),
        )),
    ]

    for cls, obj in objs:
        mj = json.dumps(msh.marshal(obj, cls))
        obj2: ta.Any = msh.unmarshal(json.loads(mj), cls)
        assert obj2 == obj


# The semantic event family is dotted-tag polymorphic ('response.output_text.delta', ...); each member must round-trip
# through the abstract base with its tag preserved.
@pytest.mark.parametrize(('tag', 'kwargs', 'cls'), [
    (
        'response.created',
        dict(response={'id': 'r', 'object': 'response'}),
        ResponsesSseEvents.Created,
    ),
    (
        'response.completed',
        dict(response={'id': 'r', 'object': 'response'}),
        ResponsesSseEvents.Completed,
    ),
    (
        'response.output_item.added',
        dict(output_index=0, item={'type': 'function_call', 'call_id': 'c', 'name': 'n', 'arguments': ''}),
        ResponsesSseEvents.OutputItemAdded,
    ),
    (
        'response.output_text.delta',
        dict(item_id='m', output_index=0, content_index=0, delta='hi'),
        ResponsesSseEvents.OutputTextDelta,
    ),
    (
        'response.function_call_arguments.delta',
        dict(item_id='f', output_index=0, delta='{"a":1}'),
        ResponsesSseEvents.FunctionCallArgumentsDelta,
    ),
    (
        'response.reasoning_text.delta',
        dict(item_id='r', output_index=0, content_index=0, delta='because'),
        ResponsesSseEvents.ReasoningTextDelta,
    ),
    (
        'error',
        dict(message='boom', code='e'),
        ResponsesSseEvents.Error,
    ),
])
def test_marshal_events(tag, kwargs, cls):
    ev = msh.unmarshal({'type': tag, **kwargs}, ResponsesSseEvents.Event)
    assert isinstance(ev, cls)

    raw: ta.Any = msh.marshal(ev, ResponsesSseEvents.Event)
    assert raw['type'] == tag

    assert msh.unmarshal(raw, ResponsesSseEvents.Event) == ev
