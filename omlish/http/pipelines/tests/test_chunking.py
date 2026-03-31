# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import unittest

from ....io.pipelines.core import IoPipeline
from ....io.pipelines.handlers.feedback import FeedbackInboundIoPipelineHandler
from ....io.pipelines.handlers.queues import InboundQueueIoPipelineHandler
from ....io.streams.utils import ByteStreamBuffers
from ...headers import HttpHeaders
from ...versions import HttpVersion
from ..clients.responses import IoPipelineHttpResponseDechunker
from ..clients.responses import IoPipelineHttpResponseDecoder
from ..requests import IoPipelineHttpRequestAborted
from ..requests import IoPipelineHttpRequestBodyData
from ..requests import IoPipelineHttpRequestChunk
from ..requests import IoPipelineHttpRequestChunkedTrailers
from ..requests import IoPipelineHttpRequestEnd
from ..requests import IoPipelineHttpRequestEndChunk
from ..requests import IoPipelineHttpRequestHead
from ..requests import IoPipelineHttpRequestLastChunk
from ..responses import FullIoPipelineHttpResponse
from ..responses import IoPipelineHttpResponseAborted
from ..responses import IoPipelineHttpResponseBodyData
from ..responses import IoPipelineHttpResponseChunk
from ..responses import IoPipelineHttpResponseChunkedTrailers
from ..responses import IoPipelineHttpResponseEnd
from ..responses import IoPipelineHttpResponseEndChunk
from ..responses import IoPipelineHttpResponseHead
from ..responses import IoPipelineHttpResponseLastChunk
from ..servers.requests import IoPipelineHttpRequestDechunker
from ..servers.responses import IoPipelineHttpResponseChunker
from ..servers.responses import IoPipelineHttpResponseEncoder


##


class TestDechunker(unittest.TestCase):
    def test_strips_chunk_framing(self) -> None:
        dechunker = IoPipelineHttpRequestDechunker()
        channel = IoPipeline.new([
            dechunker,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = IoPipelineHttpRequestHead(
            method='POST',
            target='/upload',
            headers=HttpHeaders([('Transfer-Encoding', 'chunked')]),
        )
        channel.feed_in(head)
        channel.feed_in(IoPipelineHttpRequestChunk(5))
        channel.feed_in(IoPipelineHttpRequestBodyData(b'hello'))
        channel.feed_in(IoPipelineHttpRequestEndChunk())
        channel.feed_in(IoPipelineHttpRequestChunk(5))
        channel.feed_in(IoPipelineHttpRequestBodyData(b'world'))
        channel.feed_in(IoPipelineHttpRequestEndChunk())
        channel.feed_in(IoPipelineHttpRequestLastChunk())
        channel.feed_in(IoPipelineHttpRequestChunkedTrailers())
        channel.feed_in(IoPipelineHttpRequestEnd())

        out = ibq.drain()
        self.assertEqual(len(out), 4)
        self.assertIsInstance(out[0], IoPipelineHttpRequestHead)
        self.assertIsInstance(out[1], IoPipelineHttpRequestBodyData)
        self.assertEqual(bytes(out[1].data), b'hello')
        self.assertIsInstance(out[2], IoPipelineHttpRequestBodyData)
        self.assertEqual(bytes(out[2].data), b'world')
        self.assertIsInstance(out[3], IoPipelineHttpRequestEnd)

    def test_non_chunked_passthrough(self) -> None:
        dechunker = IoPipelineHttpRequestDechunker()
        channel = IoPipeline.new([
            dechunker,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = IoPipelineHttpRequestHead(
            method='POST',
            target='/upload',
            headers=HttpHeaders([('Content-Length', '5')]),
        )
        channel.feed_in(head)
        channel.feed_in(IoPipelineHttpRequestBodyData(b'hello'))
        channel.feed_in(IoPipelineHttpRequestEnd())

        out = ibq.drain()
        self.assertEqual(len(out), 3)
        self.assertIsInstance(out[0], IoPipelineHttpRequestHead)
        self.assertIsInstance(out[1], IoPipelineHttpRequestBodyData)
        self.assertIsInstance(out[2], IoPipelineHttpRequestEnd)

    def test_aborted_resets_state(self) -> None:
        dechunker = IoPipelineHttpRequestDechunker()
        channel = IoPipeline.new([
            dechunker,
            ibq := InboundQueueIoPipelineHandler(),
        ], IoPipeline.Config(inbound_terminal='drop'))

        # Start a chunked message
        head = IoPipelineHttpRequestHead(
            method='POST',
            target='/upload',
            headers=HttpHeaders([('Transfer-Encoding', 'chunked')]),
        )
        channel.feed_in(head)
        channel.feed_in(IoPipelineHttpRequestChunk(5))
        channel.feed_in(IoPipelineHttpRequestBodyData(b'hello'))
        channel.feed_in(IoPipelineHttpRequestAborted('disconnect'))

        out = ibq.drain()
        # Chunk should be dropped, BodyData and Aborted should pass through
        self.assertEqual(len(out), 3)
        self.assertIsInstance(out[0], IoPipelineHttpRequestHead)
        self.assertIsInstance(out[1], IoPipelineHttpRequestBodyData)
        self.assertIsInstance(out[2], IoPipelineHttpRequestAborted)

        # Next message should work normally (non-chunked)
        head2 = IoPipelineHttpRequestHead(
            method='GET',
            target='/ping',
            headers=HttpHeaders([]),
        )
        channel.feed_in(head2)
        channel.feed_in(IoPipelineHttpRequestEnd())

        out2 = ibq.drain()
        self.assertEqual(len(out2), 2)
        self.assertIsInstance(out2[0], IoPipelineHttpRequestHead)
        self.assertIsInstance(out2[1], IoPipelineHttpRequestEnd)

    def test_keep_alive_chunked_then_non_chunked(self) -> None:
        dechunker = IoPipelineHttpRequestDechunker()
        channel = IoPipeline.new([
            dechunker,
            ibq := InboundQueueIoPipelineHandler(),
        ], IoPipeline.Config(inbound_terminal='drop'))

        # First: chunked message
        channel.feed_in(IoPipelineHttpRequestHead(
            method='POST',
            target='/a',
            headers=HttpHeaders([('Transfer-Encoding', 'chunked')]),
        ))
        channel.feed_in(IoPipelineHttpRequestChunk(3))
        channel.feed_in(IoPipelineHttpRequestBodyData(b'abc'))
        channel.feed_in(IoPipelineHttpRequestEndChunk())
        channel.feed_in(IoPipelineHttpRequestLastChunk())
        channel.feed_in(IoPipelineHttpRequestChunkedTrailers())
        channel.feed_in(IoPipelineHttpRequestEnd())

        out1 = ibq.drain()
        self.assertEqual(len(out1), 3)  # Head + BodyData + End

        # Second: non-chunked message
        channel.feed_in(IoPipelineHttpRequestHead(
            method='GET',
            target='/b',
            headers=HttpHeaders([]),
        ))
        channel.feed_in(IoPipelineHttpRequestEnd())

        out2 = ibq.drain()
        self.assertEqual(len(out2), 2)  # Head + End


##


class TestChunker(unittest.TestCase):
    def _make_chunked_head(self) -> IoPipelineHttpResponseHead:
        return IoPipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Content-Type', 'text/plain'),
                ('Transfer-Encoding', 'chunked'),
            ]),
        )

    def _make_non_chunked_head(self) -> IoPipelineHttpResponseHead:
        return IoPipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Content-Length', '5'),
            ]),
        )

    def test_basic_chunking(self) -> None:
        chunker = IoPipelineHttpResponseChunker()
        channel = IoPipeline.new([
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        channel.feed_in(fbi.wrap(self._make_chunked_head()))
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseBodyData(b'hello')))
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseEnd()))

        out = channel.output.drain()
        self.assertEqual(len(out), 7)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseChunk)
        self.assertEqual(out[1].size, 5)
        self.assertIsInstance(out[2], IoPipelineHttpResponseBodyData)
        self.assertEqual(bytes(out[2].data), b'hello')
        self.assertIsInstance(out[3], IoPipelineHttpResponseEndChunk)
        self.assertIsInstance(out[4], IoPipelineHttpResponseLastChunk)
        self.assertIsInstance(out[5], IoPipelineHttpResponseChunkedTrailers)
        self.assertIsInstance(out[6], IoPipelineHttpResponseEnd)

    def test_non_chunked_passthrough(self) -> None:
        chunker = IoPipelineHttpResponseChunker()
        channel = IoPipeline.new([
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        channel.feed_in(fbi.wrap(self._make_non_chunked_head()))
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseBodyData(b'hello')))
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseEnd()))

        out = channel.output.drain()
        self.assertEqual(len(out), 3)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertIsInstance(out[2], IoPipelineHttpResponseEnd)

    def test_buffering_small_writes(self) -> None:
        chunker = IoPipelineHttpResponseChunker()
        channel = IoPipeline.new([
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        channel.feed_in(fbi.wrap(self._make_chunked_head()))
        # Many small writes - should NOT produce a chunk per byte
        for b in b'hello':
            channel.feed_in(fbi.wrap(IoPipelineHttpResponseBodyData(bytes([b]))))

        # Nothing should be emitted yet (only head)
        out_before = channel.output.drain()
        self.assertEqual(len(out_before), 1)  # Just head
        self.assertIsInstance(out_before[0], IoPipelineHttpResponseHead)

        # End flushes the buffer
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseEnd()))

        out_after = channel.output.drain()
        # Should be: Chunk(5) + BodyData(hello) + EndChunk + LastChunk + Trailers + End
        self.assertEqual(len(out_after), 10)
        self.assertIsInstance(out_after[0], IoPipelineHttpResponseChunk)
        self.assertEqual(out_after[0].size, 5)
        for i, c in enumerate(b'hello'):
            self.assertIsInstance(out_after[i + 1], IoPipelineHttpResponseBodyData)
            self.assertEqual(bytes(out_after[i + 1].data), bytes([c]))
        self.assertIsInstance(out_after[6], IoPipelineHttpResponseEndChunk)
        self.assertIsInstance(out_after[7], IoPipelineHttpResponseLastChunk)
        self.assertIsInstance(out_after[8], IoPipelineHttpResponseChunkedTrailers)
        self.assertIsInstance(out_after[9], IoPipelineHttpResponseEnd)

    def test_max_chunk_size_does_not_split(self) -> None:
        chunker = IoPipelineHttpResponseChunker(max_chunk_size=3)
        channel = IoPipeline.new([
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        channel.feed_in(fbi.wrap(self._make_chunked_head()))

        # Write 7 bytes with max_chunk_size=3: should auto-flush at 3 and 6
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseBodyData(b'abcdefg')))

        out_mid = channel.output.drain()
        # Head + Chunk(3) + BodyData(abc) + EndChunk + Chunk(3) + BodyData(def) + EndChunk
        self.assertEqual(len(out_mid), 4)
        self.assertIsInstance(out_mid[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out_mid[1], IoPipelineHttpResponseChunk)
        self.assertEqual(out_mid[1].size, 7)
        self.assertEqual(bytes(out_mid[2].data), b'abcdefg')
        self.assertIsInstance(out_mid[3], IoPipelineHttpResponseEndChunk)

        # End flushes the remaining 1 byte
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseEnd()))

        out_end = channel.output.drain()
        # Chunk(1) + BodyData(g) + EndChunk + LastChunk + Trailers + End
        self.assertEqual(len(out_end), 3)
        self.assertIsInstance(out_end[0], IoPipelineHttpResponseLastChunk)
        self.assertIsInstance(out_end[1], IoPipelineHttpResponseChunkedTrailers)
        self.assertIsInstance(out_end[2], IoPipelineHttpResponseEnd)

    def test_empty_body_chunked(self) -> None:
        chunker = IoPipelineHttpResponseChunker()
        channel = IoPipeline.new([
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        channel.feed_in(fbi.wrap(self._make_chunked_head()))
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseEnd()))

        out = channel.output.drain()
        # Head + LastChunk + Trailers + End
        self.assertEqual(len(out), 4)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseLastChunk)
        self.assertIsInstance(out[2], IoPipelineHttpResponseChunkedTrailers)
        self.assertIsInstance(out[3], IoPipelineHttpResponseEnd)

    def test_full_message_chunked(self) -> None:
        chunker = IoPipelineHttpResponseChunker()
        channel = IoPipeline.new([
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        full = FullIoPipelineHttpResponse(
            head=self._make_chunked_head(),
            body=b'hello',
        )
        channel.feed_in(fbi.wrap(full))

        out = channel.output.drain()
        # Head + Chunk(5) + BodyData(hello) + EndChunk + LastChunk + Trailers + End
        self.assertEqual(len(out), 7)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseChunk)
        self.assertEqual(out[1].size, 5)
        self.assertIsInstance(out[2], IoPipelineHttpResponseBodyData)
        self.assertEqual(bytes(out[2].data), b'hello')
        self.assertIsInstance(out[3], IoPipelineHttpResponseEndChunk)
        self.assertIsInstance(out[4], IoPipelineHttpResponseLastChunk)
        self.assertIsInstance(out[5], IoPipelineHttpResponseChunkedTrailers)
        self.assertIsInstance(out[6], IoPipelineHttpResponseEnd)

    def test_full_message_non_chunked_passthrough(self) -> None:
        chunker = IoPipelineHttpResponseChunker()
        channel = IoPipeline.new([
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        full = FullIoPipelineHttpResponse(
            head=self._make_non_chunked_head(),
            body=b'hello',
        )
        channel.feed_in(fbi.wrap(full))

        out = channel.output.drain()
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], FullIoPipelineHttpResponse)

    def test_aborted_resets_state(self) -> None:
        chunker = IoPipelineHttpResponseChunker()
        channel = IoPipeline.new([
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        channel.feed_in(fbi.wrap(self._make_chunked_head()))
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseBodyData(b'hello')))
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseAborted('disconnect')))

        out = channel.output.drain()
        # Head + Aborted (buffer cleared, no chunk framing)
        self.assertEqual(len(out), 2)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseAborted)


##


class TestChunkerEncoderIntegration(unittest.TestCase):
    def test_chunker_then_encoder(self) -> None:
        """Chunker + Encoder produces correct wire bytes."""

        chunker = IoPipelineHttpResponseChunker()
        encoder = IoPipelineHttpResponseEncoder()
        channel = IoPipeline.new([
            encoder,
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        head = IoPipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Transfer-Encoding', 'chunked'),
            ]),
        )
        channel.feed_in(fbi.wrap(head))
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseBodyData(b'hello')))
        channel.feed_in(fbi.wrap(IoPipelineHttpResponseEnd()))

        out = channel.output.drain()
        wire = b''.join(out)

        self.assertIn(b'Transfer-Encoding: chunked\r\n', wire)
        self.assertIn(b'5\r\nhello\r\n', wire)
        self.assertIn(b'0\r\n\r\n', wire)


class TestDechunkerDecoderIntegration(unittest.TestCase):
    def test_decoder_then_dechunker(self) -> None:
        """Decoder + Dechunker strips chunk framing from wire bytes."""

        decoder = IoPipelineHttpResponseDecoder()
        dechunker = IoPipelineHttpResponseDechunker()
        channel = IoPipeline.new([
            decoder,
            dechunker,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        wire = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
            b'5\r\nhello\r\n'
            b'5\r\nworld\r\n'
            b'0\r\n\r\n'
        )
        channel.feed_in(wire)

        out = ibq.drain()
        self.assertEqual(len(out), 4)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertEqual(ByteStreamBuffers.to_bytes(out[1].data), b'hello')
        self.assertIsInstance(out[2], IoPipelineHttpResponseBodyData)
        self.assertEqual(ByteStreamBuffers.to_bytes(out[2].data), b'world')
        self.assertIsInstance(out[3], IoPipelineHttpResponseEnd)


class TestRoundTrip(unittest.TestCase):
    def test_encode_decode_round_trip(self) -> None:
        """Chunker+Encoder → Decoder+Dechunker round-trips correctly."""

        # Encode
        chunker = IoPipelineHttpResponseChunker()
        encoder = IoPipelineHttpResponseEncoder()
        enc_channel = IoPipeline.new([
            encoder,
            chunker,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        head = IoPipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Transfer-Encoding', 'chunked'),
            ]),
        )
        enc_channel.feed_in(fbi.wrap(head))
        enc_channel.feed_in(fbi.wrap(IoPipelineHttpResponseBodyData(b'hello')))
        enc_channel.feed_in(fbi.wrap(IoPipelineHttpResponseBodyData(b'world')))
        enc_channel.feed_in(fbi.wrap(IoPipelineHttpResponseEnd()))

        wire = b''.join(enc_channel.output.drain())

        # Decode
        decoder = IoPipelineHttpResponseDecoder()
        dechunker = IoPipelineHttpResponseDechunker()
        dec_channel = IoPipeline.new([
            decoder,
            dechunker,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        dec_channel.feed_in(wire)

        out = ibq.drain()
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertEqual(out[0].status, 200)

        body = b''.join(ByteStreamBuffers.to_bytes(m.data) for m in out[1:-1])
        self.assertEqual(body, b'helloworld')

        self.assertIsInstance(out[-1], IoPipelineHttpResponseEnd)
