import os.path

from omlish import check
from omlish import marshal as msh
from omlish.formats import json
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from ......backends.anthropic.protocol.sse.events import AnthropicSseDecoderEvents
from .....chat.stream.types import AiChoiceDelta
from .....chat.stream.types import AiMessageDelta


def test_assemble():
    with open(os.path.join(
            os.path.dirname(__file__),
            '../../../../../backends/anthropic/protocol/sse/tests/story.txt',  # >_<
    ), 'rb') as f:
        src_b = f.read()

    def run(bs):
        msg_start: AnthropicSseDecoderEvents.MessageStart | None = None
        cbk_start: AnthropicSseDecoderEvents.ContentBlockStart | None = None
        msg_stop: AnthropicSseDecoderEvents.MessageStop | None = None

        db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])

        sd = sse.SseDecoder()
        for b in bs:
            for l in db.feed(b):
                if isinstance(l, DelimitingBuffer.Incomplete):
                    # FIXME: handle
                    return []

                # FIXME: https://docs.anthropic.com/en/docs/build-with-claude/streaming
                for so in sd.process_line(l):
                    if isinstance(so, sse.SseEvent):
                        ss = so.data.decode('utf-8')
                        if ss == '[DONE]':
                            return []

                        dct = json.loads(ss)
                        check.equal(dct['type'], so.type.decode('utf-8'))
                        ae = msh.unmarshal(dct, AnthropicSseDecoderEvents.Event)

                        match ae:
                            case AnthropicSseDecoderEvents.MessageStart():
                                check.none(msg_start)
                                msg_start = ae
                                if msg_start.message.content:
                                    raise NotImplementedError

                            case AnthropicSseDecoderEvents.ContentBlockStart():
                                check.not_none(msg_start)
                                check.none(cbk_start)
                                cbk_start = ae
                                if isinstance(ae.content_block, AnthropicSseDecoderEvents.ContentBlockStart.Text):
                                    yield [AiChoiceDelta(AiMessageDelta(
                                        ae.content_block.text,
                                    ))]
                                else:
                                    raise TypeError(ae.content_block)

                            case AnthropicSseDecoderEvents.ContentBlockDelta():
                                check.not_none(cbk_start)
                                if isinstance(ae.delta, AnthropicSseDecoderEvents.ContentBlockDelta.TextDelta):
                                    yield [AiChoiceDelta(AiMessageDelta(
                                        ae.delta.text,
                                    ))]
                                else:
                                    raise TypeError(ae.delta)

                            case AnthropicSseDecoderEvents.ContentBlockStop():
                                check.not_none(cbk_start)
                                cbk_start = None

                            case AnthropicSseDecoderEvents.MessageDelta():
                                check.not_none(msg_start)
                                check.none(cbk_start)

                            case AnthropicSseDecoderEvents.MessageStop():
                                check.not_none(msg_start)
                                check.none(msg_stop)
                                msg_stop = ae

                            case AnthropicSseDecoderEvents.Ping():
                                pass

                            case _:
                                raise TypeError(ae)

    for m in run([src_b]):
        print(m)
