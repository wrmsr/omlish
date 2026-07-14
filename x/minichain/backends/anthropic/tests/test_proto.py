# ruff: noqa: SLF001
"""Offline coverage of the anthropic request/response translation and option handling."""
from omcore import check

from .....backends.anthropic.protocol import types as pt
from ....chat.choices.services import ChatChoicesRequest
from ....chat.messages import AiMessage
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.tools.types import Tool
from ....llms.stopreasons import EndTurnStopReason
from ....llms.stopreasons import MaxTokensStopReason
from ....llms.stopreasons import StopSequenceStopReason
from ....llms.stopreasons import ToolUseStopReason
from ....llms.types import MaxTokens
from ....llms.types import Temperature
from ....llms.types import TokenUsageOutput
from ....standard import ApiKey
from ....tools.types import ToolSpec
from ....tools.types import ToolUse
from ....tools.types import ToolUseResult
from ..chat import AnthropicChatChoicesService
from ..protocol import build_ant_request_messages
from ..protocol import build_ant_request_tool
from ..protocol import build_mc_choices_response
from ..protocol import build_mc_stop_reason


##


def test_build_request_messages_system_hoisted():
    built = build_ant_request_messages([
        SystemMessage('be nice'),
        UserMessage('hi'),
        AiMessage('hello'),
        ToolUseMessage(ToolUse(id='call_1', name='weather', args={'location': 'Tokyo'})),
        ToolUseResultMessage(ToolUseResult(id='call_1', name='weather', c='sunny')),
    ])

    # System is hoisted out of the message list.
    assert built.system == [pt.Text('be nice')]
    assert [m.role for m in built.messages] == ['user', 'assistant', 'assistant', 'user']

    tu_msg = built.messages[2]
    tu = check.isinstance(check.single(check.isinstance(tu_msg.content, list)), pt.ToolUse)
    assert tu.id == 'call_1'
    assert tu.name == 'weather'
    assert tu.input == {'location': 'Tokyo'}

    tr_msg = built.messages[3]
    tr = check.isinstance(check.single(check.isinstance(tr_msg.content, list)), pt.ToolResult)
    assert tr.tool_use_id == 'call_1'
    assert tr.content == 'sunny'


def test_build_request_tool_flat():
    ts = build_ant_request_tool(Tool(ToolSpec('weather', desc='get weather')))
    assert ts.name == 'weather'
    assert ts.description == 'get weather'
    assert ts.input_schema is not None


def test_build_request_honors_options_and_default_max_tokens():
    svc = AnthropicChatChoicesService(ApiKey('k'))

    # Explicit options consumed.
    req = svc._build_request(ChatChoicesRequest([UserMessage('hi')], [Temperature(.25), MaxTokens(123)]))
    assert req.temperature == .25
    assert req.max_tokens == 123
    assert req.stream is None
    assert req.model == 'claude-haiku-4-5'

    # The mandatory max_tokens defaults when unspecified.
    req2 = svc._build_request(ChatChoicesRequest([UserMessage('hi')]))
    assert req2.max_tokens == 4096

    # Stream flag set when requested.
    req3 = svc._build_request(ChatChoicesRequest([UserMessage('hi')]), stream=True)
    assert req3.stream is True


def test_build_choices_response():
    msg = pt.Message(
        role='assistant',
        content=[
            pt.Text('hello there'),
            pt.ToolUse(id='call_1', name='weather', input={'location': 'Tokyo'}),
        ],
        usage=pt.Usage(input_tokens=11, output_tokens=22),
    )

    out = build_mc_choices_response(msg)

    gen = check.single(out.v.gs)
    chat = gen.chat
    assert [type(m) for m in chat] == [AiMessage, ToolUseMessage]
    assert check.isinstance(chat[0], AiMessage).c == 'hello there'
    tu = check.isinstance(chat[1], ToolUseMessage).tu
    assert tu.id == 'call_1'
    assert tu.name == 'weather'
    assert tu.args == {'location': 'Tokyo'}

    tuo = check.not_none(gen.outputs.get(TokenUsageOutput))
    assert tuo.v.input == 11
    assert tuo.v.output == 22
    assert tuo.v.total == 33


def test_stop_reason_mapping():
    assert build_mc_stop_reason(None) is None
    assert isinstance(build_mc_stop_reason('end_turn'), EndTurnStopReason)
    assert isinstance(build_mc_stop_reason('max_tokens'), MaxTokensStopReason)
    assert isinstance(build_mc_stop_reason('tool_use'), ToolUseStopReason)
    assert isinstance(build_mc_stop_reason('stop_sequence'), StopSequenceStopReason)
