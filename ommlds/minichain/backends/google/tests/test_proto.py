# ruff: noqa: SLF001
"""Offline coverage of the google (gemini) chat backend: request/response/stream translation through the real joiner."""
from omlish import check

from .....backends.google.protocol import types as pt
from ....chat.choices.services import ChatChoicesRequest
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import UserMessage
from ....chat.metadata import ThoughtSignature
from ....chat.stream.joining import AiDeltaJoiner
from ....chat.tools.types import Tool
from ....llms.stopreasons import ContentFilterStopReason
from ....llms.stopreasons import EndTurnStopReason
from ....llms.stopreasons import MaxTokensStopReason
from ....standard import ApiKey
from ....tools.types import ToolSpec
from ..chat import GoogleChatChoicesService
from ..protocol import build_g_request_content
from ..protocol import build_g_request_tool
from ..protocol import build_mc_ai_choices_deltas
from ..protocol import build_mc_choices_response
from ..protocol import build_mc_stop_reason
from ..protocol import pop_g_system_instruction


##


def test_build_request_and_system_pop():
    msgs: list[Message] = [
        SystemMessage('be nice'),
        UserMessage('hi'),
    ]
    sys_inst = pop_g_system_instruction(msgs)
    assert check.not_none(check.not_none(sys_inst).parts)[0].text == 'be nice'
    assert [m.role for m in [build_g_request_content(m) for m in msgs]] == ['user']


def test_build_request_tool():
    g_tool = build_g_request_tool(Tool(ToolSpec('weather', desc='get weather')))
    fd = check.single(check.not_none(g_tool.function_declarations))
    assert fd.name == 'weather'


def test_request_url_and_contents():
    svc = GoogleChatChoicesService(ApiKey('k'))
    g_req = svc._build_request(ChatChoicesRequest([SystemMessage('sys'), UserMessage('hi')]))

    # System is hoisted; remaining content is the user turn.
    assert check.not_none(check.not_none(g_req.system_instruction).parts)[0].text == 'sys'
    assert [c.role for c in check.not_none(g_req.contents)] == ['user']

    url = svc._build_url('generateContent')
    assert ':generateContent?key=k' in url
    assert url.startswith('https://generativelanguage.googleapis.com')

    surl = svc._build_url('streamGenerateContent', query='alt=sse')
    assert ':streamGenerateContent?alt=sse&key=k' in surl


def test_build_choices_response():
    resp = pt.GenerateContentResponse(candidates=[
        pt.GenerateContentResponse.Candidate(content=pt.Content(parts=[
            pt.Part(text='hello there'),
            pt.Part(function_call=pt.FunctionCall(id='c1', name='weather', args={'location': 'Tokyo'})),
        ])),
    ])

    out = build_mc_choices_response(resp)
    chat = check.single(out.v).chat
    assert [type(m) for m in chat] == [AiMessage, ToolUseMessage]
    assert check.isinstance(chat[0], AiMessage).c == 'hello there'
    tu = check.isinstance(chat[1], ToolUseMessage).tu
    assert tu.name == 'weather'
    assert tu.args == {'location': 'Tokyo'}


def _resp(*parts: pt.Part) -> pt.GenerateContentResponse:
    return pt.GenerateContentResponse(candidates=[
        pt.GenerateContentResponse.Candidate(content=pt.Content(parts=list(parts))),
    ])


def test_stream_join_and_thought_signature():
    chunks = [
        _resp(pt.Part(text='hel')),
        _resp(pt.Part(text='lo there')),
        _resp(pt.Part(
            function_call=pt.FunctionCall(id='c1', name='weather', args={'location': 'Tokyo'}),
            thought_signature='sig123',
        )),
    ]

    joiner = AiDeltaJoiner()
    for resp in chunks:
        for ds in build_mc_ai_choices_deltas(resp):
            joiner.add(check.single(ds.choices).deltas)

    joined = joiner.build()
    assert [type(m) for m in joined] == [AiMessage, ToolUseMessage]
    assert check.isinstance(joined[0], AiMessage).c == 'hello there'
    tum = check.isinstance(joined[1], ToolUseMessage)
    assert tum.tu.name == 'weather'
    # The thought signature on the function-call part rides through to the joined message's metadata.
    assert check.not_none(tum.metadata.get(ThoughtSignature)).v == 'sig123'


def test_stop_reason_mapping():
    assert build_mc_stop_reason(None) is None
    assert isinstance(build_mc_stop_reason('STOP'), EndTurnStopReason)
    assert isinstance(build_mc_stop_reason('MAX_TOKENS'), MaxTokensStopReason)
    assert isinstance(build_mc_stop_reason('SAFETY'), ContentFilterStopReason)
