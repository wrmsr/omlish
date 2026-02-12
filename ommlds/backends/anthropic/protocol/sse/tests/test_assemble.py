import os.path

from omlish import check
from omlish import marshal as msh
from omlish.formats import json
from omlish.http import sse
from omlish.io.streams.framing import LongestMatchDelimiterByteStreamFrameDecoder
from omlish.io.streams.segmented import SegmentedByteStreamBuffer

from ...types import Message
from ..assemble import AnthropicSseMessageAssembler
from ..events import AnthropicSseDecoderEvents


def test_assemble():
    with open(os.path.join(os.path.dirname(__file__), 'story.txt'), 'rb') as f:
        src_b = f.read()

    def run(bs):
        buf = SegmentedByteStreamBuffer(chunk_size=0x4000)
        frm = LongestMatchDelimiterByteStreamFrameDecoder([b'\r', b'\n', b'\r\n'])

        sd = sse.SseDecoder()
        ass = AnthropicSseMessageAssembler()
        for b in bs:
            buf.write(b)
            for l in frm.decode(buf, final=not b):
                # FIXME: https://docs.anthropic.com/en/docs/build-with-claude/streaming
                for so in sd.process_line(l.tobytes()):
                    if isinstance(so, sse.SseEvent):
                        ss = so.data.decode('utf-8')
                        if ss == '[DONE]':
                            return []

                        dct = json.loads(ss)
                        check.equal(dct['type'], so.type.decode('utf-8'))
                        ae = msh.unmarshal(dct, AnthropicSseDecoderEvents.Event)

                        for am in ass(ae):
                            if isinstance(am, Message):
                                yield am

            if not b and len(buf):
                # FIXME: handle
                return []

    for m in run([src_b]):
        print(m)
