"""
Offline coverage of the anthropic streaming translation: the real captured event story (`story.txt`) and a
hand-authored tool-use sequence, each driven through `AnthropicSseDeltaTranslator` and the real `AiDeltaJoiner`.
"""
import os.path
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish.formats.json import all as json
from omlish.http import sse
from omlish.io.streams.framing import LongestMatchDelimiterByteStreamFrameDecoder
from omlish.io.streams.segmented import SegmentedByteStreamBuffer

from .....backends.anthropic.protocol.sse.events import AnthropicSseDecoderEvents
from ....chat.messages import AiMessage
from ....chat.messages import ToolUseMessage
from ....chat.stream.joining import AiDeltaJoiner
from ..protocol import AnthropicSseDeltaTranslator


##


def _decode_events(src: bytes) -> list[AnthropicSseDecoderEvents.Event]:
    buf = SegmentedByteStreamBuffer(chunk_size=0x4000)
    frm = LongestMatchDelimiterByteStreamFrameDecoder([b'\r', b'\n', b'\r\n'])
    sd = sse.SseDecoder()

    out: list[AnthropicSseDecoderEvents.Event] = []
    for b in [src, b'']:
        buf.write(b)
        for l in frm.decode(buf, final=not b):
            for so in sd.process_line(l.tobytes()):
                if isinstance(so, sse.SseEvent):
                    dct = json.loads(so.data.decode('utf-8'))
                    check.equal(dct['type'], so.type.decode('utf-8'))
                    out.append(msh.unmarshal(dct, AnthropicSseDecoderEvents.Event))
    return out


def test_translate_story():
    with open(os.path.join(
            os.path.dirname(__file__),
            '../../../../backends/anthropic/protocol/sse/tests/story.txt',
    ), 'rb') as f:
        src_b = f.read()

    translator = AnthropicSseDeltaTranslator()
    joiner = AiDeltaJoiner()
    done = False
    for ev in _decode_events(src_b):
        res = translator.translate(ev)
        if res.deltas:
            joiner.add(res.deltas)
        if res.done:
            done = True

    assert done
    translator.finish()

    joined = joiner.build()
    assert [type(m) for m in joined] == [AiMessage]
    text = check.isinstance(joined[0], AiMessage).c
    assert isinstance(text, str)
    assert text.startswith('## The Backpack at the Yard Sale')
    assert len(text) > 100


##


def _event(dct: dict[str, ta.Any]) -> AnthropicSseDecoderEvents.Event:
    return msh.unmarshal(dct, AnthropicSseDecoderEvents.Event)


def test_translate_tool_use():
    events = [
        _event({'type': 'message_start', 'message': {
            'id': 'msg_1', 'role': 'assistant', 'model': 'claude', 'content': [],
        }}),
        _event({'type': 'content_block_start', 'index': 0, 'content_block': {
            'type': 'tool_use', 'id': 'toolu_1', 'name': 'get_weather', 'input': {},
        }}),
        _event({'type': 'content_block_delta', 'index': 0, 'delta': {
            'type': 'input_json_delta', 'partial_json': '{"location":',
        }}),
        _event({'type': 'content_block_delta', 'index': 0, 'delta': {
            'type': 'input_json_delta', 'partial_json': '"Tokyo"}',
        }}),
        _event({'type': 'content_block_stop', 'index': 0}),
        _event({'type': 'message_delta', 'delta': {'stop_reason': 'tool_use', 'stop_sequence': None},
                'usage': {'output_tokens': 5}}),
        _event({'type': 'message_stop'}),
    ]

    translator = AnthropicSseDeltaTranslator()
    joiner = AiDeltaJoiner()
    done = False
    for ev in events:
        res = translator.translate(ev)
        if res.deltas:
            joiner.add(res.deltas)
        if res.done:
            done = True

    assert done
    translator.finish()

    joined = joiner.build()
    assert [type(m) for m in joined] == [ToolUseMessage]
    tu = check.isinstance(joined[0], ToolUseMessage).tu
    assert tu.id == 'toolu_1'
    assert tu.name == 'get_weather'
    assert tu.args == {'location': 'Tokyo'}
