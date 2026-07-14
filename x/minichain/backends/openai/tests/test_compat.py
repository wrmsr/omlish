# ruff: noqa: SLF001
"""
Offline coverage of the openai-compat dialect core: option handling in request assembly, the SSE envelope, delta
translation fidelity through the real joiner, dialect-extension behavior (reasoning channels), and the per-vendor
knob subclassing - everything short of the network itself (which the @online smokes cover).
"""
import json
import typing as ta

import pytest

from omcore import check
from omcore import marshal as msh
from omcore.http import sse

from .....backends.openai import protocol as pt
from ....chat.messages import AiMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import UserMessage
from ....chat.stream.joining import AiDeltaJoiner
from ....llms.stopreasons import ContentFilterStopReason
from ....llms.stopreasons import EndTurnStopReason
from ....llms.stopreasons import MaxTokensStopReason
from ....llms.stopreasons import OtherStopReason
from ....llms.stopreasons import ToolUseStopReason
from ....llms.types import MaxTokens
from ....llms.types import Temperature
from ....standard import ApiKey
from ...cerebras.chat import CerebrasChatChoicesService
from ...cerebras.stream import CerebrasChatChoicesStreamService
from ...groq.chat import GroqChatChoicesService
from ...groq.stream import GroqChatChoicesStreamService
from ..compat import OpenaiCompatChatChoicesServiceBase
from ..protocol import OpenaiChatRequestHandler
from ..protocol import build_mc_stop_reason
from ..stream import OpenaiChatChoicesStreamService


##


def test_request_handler_honors_options():
    rh = OpenaiChatRequestHandler(
        [UserMessage('hi')],
        Temperature(.25),
        MaxTokens(123),
        model='gpt-whatever',
    )

    req = rh.oai_request()
    assert req.temperature == .25
    assert req.max_tokens == 123
    assert req.model == 'gpt-whatever'
    assert check.isinstance(next(iter(req.messages)), pt.UserChatCompletionMessage).content == 'hi'


##


def _chunk_bytes(**kwargs: ta.Any) -> bytes:
    return json.dumps({
        'id': 'chatcmpl-x',
        'object': 'chat.completion.chunk',
        'created': 1,
        'model': 'm',
        **kwargs,
    }).encode('utf-8')


def _content_chunk(s: str) -> bytes:
    return _chunk_bytes(choices=[{'index': 0, 'delta': {'content': s}}])


def _sse(data: bytes) -> sse.SseEvent:
    return sse.SseEvent(b'message', data)


@pytest.mark.asyncs('asyncio')
async def test_stream_envelope_and_join():
    svc = OpenaiChatChoicesStreamService(ApiKey('k'))
    rh = svc._ResponseHandler(svc)

    raw: list[bytes] = [
        _chunk_bytes(choices=[{'index': 0, 'delta': {'role': 'assistant', 'content': ''}}]),
        _content_chunk('hel'),
        _content_chunk('lo there'),
        _chunk_bytes(choices=[{'index': 0, 'delta': {'tool_calls': [
            {'index': 0, 'id': 'call_1', 'type': 'function', 'function': {'name': 'weather', 'arguments': ''}},
        ]}}]),
        _chunk_bytes(choices=[{'index': 0, 'delta': {'tool_calls': [
            {'index': 0, 'function': {'arguments': '{"location":'}},
        ]}}]),
        _chunk_bytes(choices=[{'index': 0, 'delta': {'tool_calls': [
            {'index': 0, 'function': {'arguments': '"Tokyo"}'}},
        ]}}]),
        _chunk_bytes(choices=[{'index': 0, 'delta': {}, 'finish_reason': 'tool_calls'}]),
        b'[DONE]',
    ]

    joiner = AiDeltaJoiner()
    done = False
    for b in raw:
        for out in await rh.process_sse(_sse(b)):
            if out is None:
                done = True
                break
            joiner.add(check.single(out.choices).deltas)
        if done:
            break

    assert done

    joined = joiner.build()
    assert [type(m) for m in joined] == [AiMessage, ToolUseMessage]
    assert check.isinstance(joined[0], AiMessage).c == 'hello there'
    tu = check.isinstance(joined[1], ToolUseMessage).tu
    assert tu.id == 'call_1'
    assert tu.name == 'weather'
    assert tu.args == {'location': 'Tokyo'}


@pytest.mark.asyncs('asyncio')
async def test_stream_reasoning_channel_skipped():
    svc = GroqChatChoicesStreamService(ApiKey('k'))
    rh = svc._ResponseHandler(svc)

    out = await rh.process_sse(_sse(_chunk_bytes(choices=[
        {'index': 0, 'delta': {'channel': 'analysis', 'content': 'thinking out loud'}},
    ])))

    (deltas,) = out
    assert deltas is not None
    assert list(check.single(deltas.choices).deltas) == []

    # And non-message sse outputs are ignored entirely.
    assert await rh.process_sse(sse.SseComment(b'hi')) == []


def test_dialect_fields_round_trip():
    sj = json.loads(_chunk_bytes(choices=[
        {'index': 0, 'delta': {'channel': 'commentary', 'content': 'x'}},
    ]).decode('utf-8'))

    ccc = msh.unmarshal(sj, pt.ChatCompletionChunk)
    assert ccc.choices[0].delta.channel == 'commentary'

    rm = msh.unmarshal({'role': 'assistant', 'content': 'hi', 'reasoning': 'because'}, pt.ChatCompletionResponseMessage)  # noqa
    assert rm.reasoning == 'because'


##


@pytest.mark.parametrize(
    ('svc_cls', 'url_part', 'env'),
    [
        (GroqChatChoicesService, 'api.groq.com/openai', 'GROQ_API_KEY'),
        (GroqChatChoicesStreamService, 'api.groq.com/openai', 'GROQ_API_KEY'),
        (CerebrasChatChoicesService, 'api.cerebras.ai', 'CEREBRAS_API_KEY'),
        (CerebrasChatChoicesStreamService, 'api.cerebras.ai', 'CEREBRAS_API_KEY'),
    ],
)
def test_vendor_knobs(svc_cls, url_part, env):
    assert issubclass(svc_cls, OpenaiCompatChatChoicesServiceBase)
    assert url_part in svc_cls.URL
    assert svc_cls.API_KEY_ENV == env
    assert svc_cls.EXTRA_HEADERS
    assert svc_cls.MODEL_NAMES.default is not None
    assert svc_cls.DEFAULT_MODEL_NAME.v == svc_cls.MODEL_NAMES.default

    svc = svc_cls(ApiKey('k'))
    hdrs = svc._build_headers()
    assert any(b'Bearer k' in (v if isinstance(v, bytes) else str(v).encode()) for v in hdrs.values())


def test_stop_reason_mapping():
    assert isinstance(build_mc_stop_reason('stop'), EndTurnStopReason)
    assert isinstance(build_mc_stop_reason('length'), MaxTokensStopReason)
    assert isinstance(build_mc_stop_reason('tool_calls'), ToolUseStopReason)
    assert isinstance(build_mc_stop_reason('content_filter'), ContentFilterStopReason)
    assert check.isinstance(build_mc_stop_reason('weird'), OtherStopReason).raw == 'weird'
