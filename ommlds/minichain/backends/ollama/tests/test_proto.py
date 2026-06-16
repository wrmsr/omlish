# ruff: noqa: SLF001
"""Offline coverage of the ollama native chat backend: request/response/stream translation through the real joiner."""
import json

import pytest

from omlish import check

from .....backends.ollama import protocol as pt
from ....chat.messages import AiMessage
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.stream.joining import AiDeltaJoiner
from ....chat.tools.types import Tool
from ....llms.stopreasons import EndTurnStopReason
from ....llms.stopreasons import MaxTokensStopReason
from ....tools.types import ToolSpec
from ....tools.types import ToolUse
from ....tools.types import ToolUseResult
from ..protocol import build_mc_choices_response
from ..protocol import build_mc_stop_reason
from ..protocol import build_ol_request_messages
from ..protocol import build_ol_request_tool
from ..stream import OllamaChatChoicesStreamService


##


def test_build_request_messages():
    msgs = build_ol_request_messages([
        SystemMessage('be nice'),
        UserMessage('weather in tokyo?'),
        ToolUseMessage(ToolUse(id='call_1', name='weather', args={'location': 'Tokyo'})),
        ToolUseResultMessage(ToolUseResult(id='call_1', name='weather', c='sunny')),
        AiMessage('it is sunny'),
    ])

    assert [m.role for m in msgs] == ['system', 'user', 'assistant', 'tool', 'assistant']

    tu_msg = msgs[2]
    tc = check.single(check.not_none(tu_msg.tool_calls))
    assert tc.id == 'call_1'
    assert tc.function.name == 'weather'
    assert tc.function.arguments == {'location': 'Tokyo'}

    tool_msg = msgs[3]
    assert tool_msg.tool_name == 'weather'
    assert tool_msg.content == 'sunny'


def test_build_request_tool():
    t = build_ol_request_tool(Tool(ToolSpec('weather', desc='get weather')))
    fn = check.not_none(t.function)
    assert fn.name == 'weather'
    assert fn.description == 'get weather'
    assert fn.parameters is not None


def test_build_choices_response():
    resp = pt.ChatResponse(
        model='llama3.2',
        done=True,
        message=pt.Message(
            role='assistant',
            content='hello there',
            tool_calls=[pt.Message.ToolCall(
                id='call_1',
                function=pt.Message.ToolCall.Function(name='weather', arguments={'location': 'Tokyo'}),
            )],
        ),
    )

    out = build_mc_choices_response(resp)

    chat = check.single(out.v.gs).chat
    assert [type(m) for m in chat] == [AiMessage, ToolUseMessage]
    assert check.isinstance(chat[0], AiMessage).c == 'hello there'
    tu = check.isinstance(chat[1], ToolUseMessage).tu
    assert tu.id == 'call_1'
    assert tu.name == 'weather'
    assert tu.args == {'location': 'Tokyo'}


##


def _line(message: dict, **kwargs) -> bytes:
    return json.dumps({'model': 'llama3.2', 'message': message, **kwargs}).encode('utf-8')


@pytest.mark.asyncs('asyncio')
async def test_stream_join():
    svc = OllamaChatChoicesStreamService()
    rh = svc._ResponseHandler(svc)

    # Ollama's native stream is JSONL; tool calls arrive complete (not as partial-arg deltas).
    raw: list[bytes] = [
        _line({'role': 'assistant', 'content': 'hel'}, done=False),
        _line({'role': 'assistant', 'content': 'lo there'}, done=False),
        _line({'role': 'assistant', 'tool_calls': [
            {'id': 'call_1', 'function': {'name': 'weather', 'arguments': {'location': 'Tokyo'}}},
        ]}, done=False),
        _line({'role': 'assistant', 'content': ''}, done=True, done_reason='stop'),
    ]

    joiner = AiDeltaJoiner()
    for b in raw:
        for out in await rh.process_line(b):
            joiner.add(check.single(out.choices).deltas)

    joined = joiner.build()
    assert [type(m) for m in joined] == [AiMessage, ToolUseMessage]
    assert check.isinstance(joined[0], AiMessage).c == 'hello there'
    tu = check.isinstance(joined[1], ToolUseMessage).tu
    assert tu.id == 'call_1'
    assert tu.name == 'weather'
    assert tu.args == {'location': 'Tokyo'}


def test_stop_reason_mapping():
    assert build_mc_stop_reason(None) is None
    assert isinstance(build_mc_stop_reason('stop'), EndTurnStopReason)
    assert isinstance(build_mc_stop_reason('length'), MaxTokensStopReason)
