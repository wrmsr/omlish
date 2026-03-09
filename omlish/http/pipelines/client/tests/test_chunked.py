# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import unittest

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.handlers.queues import InboundQueueIoPipelineHandler
from .....io.streams.utils import ByteStreamBuffers
from ...decoders import IoPipelineHttpDecodingConfig
from ...responses import IoPipelineHttpResponseAborted
from ...responses import IoPipelineHttpResponseBodyData
from ...responses import IoPipelineHttpResponseEnd
from ...responses import IoPipelineHttpResponseHead
from ..responses import IoPipelineHttpResponseDecoder


class TestPipelineHttpResponseDecoder(unittest.TestCase):
    def test_simple_chunked_response(self) -> None:
        """Test decoding simple chunked response."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        # Send response head with chunked encoding
        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Send chunked body: 5\r\nhello\r\n5\r\nworld\r\n0\r\n\r\n
        channel.feed_in(b'5\r\nhello\r\n5\r\nworld\r\n0\r\n\r\n')

        out = ibq.drain()

        # Should get: head, chunk1 data, chunk2 data, end marker
        self.assertEqual(len(out), 4)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertEqual(ByteStreamBuffers.to_bytes(out[1].data), b'hello')
        self.assertIsInstance(out[2], IoPipelineHttpResponseBodyData)
        self.assertEqual(ByteStreamBuffers.to_bytes(out[2].data), b'world')
        self.assertIsInstance(out[3], IoPipelineHttpResponseEnd)

    def test_chunked_response_split_across_reads(self) -> None:
        """Test chunked response split across multiple reads."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Send chunk size
        channel.feed_in(b'5\r\n')

        # Send partial chunk data
        channel.feed_in(b'hel')

        # Send rest of chunk data + trailing
        channel.feed_in(b'lo\r\n')

        # Send final chunk
        channel.feed_in(b'0\r\n\r\n')

        out = ibq.drain()

        # Should get: head, chunk data, end marker
        self.assertEqual(len(out), 4)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[1].data, b'hel')
        self.assertIsInstance(out[2], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[2].data, b'lo')
        self.assertIsInstance(out[3], IoPipelineHttpResponseEnd)

    def test_non_chunked_response_passes_through(self) -> None:
        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Length: 5\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Send body (not chunked)
        channel.feed_in(b'hello')

        out = ibq.drain()

        # Should pass through unchanged
        self.assertEqual(len(out), 3)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[1].data, b'hello')
        self.assertIsInstance(out[2], IoPipelineHttpResponseEnd)

    def test_empty_chunks_skipped(self) -> None:
        """Test that zero-size chunks before final chunk work correctly."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Single chunk then terminator
        channel.feed_in(b'5\r\nhello\r\n0\r\n\r\n')

        out = ibq.drain()

        self.assertEqual(len(out), 3)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[1].data, b'hello')
        self.assertIsInstance(out[2], IoPipelineHttpResponseEnd)

    def test_large_chunk(self) -> None:
        """Test decoding large chunk."""

        # Use larger buffer size for this test
        decoder = IoPipelineHttpResponseDecoder(
            config=dc.replace(
                IoPipelineHttpDecodingConfig.DEFAULT,
                chunk_header_buffer=dc.replace(
                    IoPipelineHttpDecodingConfig.DEFAULT.chunk_header_buffer,
                    max_size=64 * 1024,
                ),
            ),
        )
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # 1KB chunk
        data = b'x' * 1024
        chunk_size = f'{len(data):x}\r\n'.encode('ascii')

        channel.feed_in(chunk_size + data + b'\r\n0\r\n\r\n')

        out = ibq.drain()

        self.assertEqual(len(out), 3)
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[1].data, data)
        self.assertIsInstance(out[2], IoPipelineHttpResponseEnd)

    def test_hex_chunk_sizes(self) -> None:
        """Test that hex chunk sizes are properly decoded."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Use hex sizes: a (10), 10 (16), 64 (100)
        channel.feed_in(
            b'a\r\n' + b'0123456789' + b'\r\n' +
            b'10\r\n' + b'a' * 16 + b'\r\n' +
            b'64\r\n' + b'b' * 100 + b'\r\n' +
            b'0\r\n\r\n',
        )

        out = ibq.drain()

        self.assertEqual(len(out), 5)  # head + 3 chunks + end
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[1].data, b'0123456789')
        self.assertIsInstance(out[2], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[2].data, b'a' * 16)
        self.assertIsInstance(out[3], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[3].data, b'b' * 100)
        self.assertIsInstance(out[4], IoPipelineHttpResponseEnd)

    def test_eof_before_complete_raises(self) -> None:
        """Test that EOF before chunked encoding completes raises error."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Send partial chunk
        channel.feed_in(b'5\r\nhel')

        # Send EOF before completion - pipeline wraps exception in Error event
        channel.feed_in(IoPipelineMessages.FinalInput())

        out = ibq.drain()

        # Should get an aborted message
        out_head, chunk, aborted, eof = out
        self.assertIsInstance(out_head, IoPipelineHttpResponseHead)
        self.assertIsInstance(chunk, IoPipelineHttpResponseBodyData)
        self.assertEqual(chunk.data.tobytes(), b'hel')
        self.assertIsInstance(aborted, IoPipelineHttpResponseAborted)
        self.assertIsInstance(eof, IoPipelineMessages.FinalInput)

    def test_invalid_chunk_size_raises(self) -> None:
        """Test that invalid chunk size raises error."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Send invalid chunk size - pipeline wraps exception in Error event
        channel.feed_in(b'xyz\r\n')

        out = ibq.drain()

        # Should get head and Error event
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseAborted)
        self.assertIn('Invalid chunk size', out[1].reason_str)

    def test_missing_trailing_crlf_raises(self) -> None:
        """Test that missing trailing CRLF after chunk data raises error."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Send chunk with missing trailing \r\n - pipeline wraps exception in Error event
        channel.feed_in(b'5\r\nhelloXX')

        out = ibq.drain()

        # Should get head and Error event
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[1].data.tobytes(), b'hello')
        self.assertIsInstance(out[2], IoPipelineHttpResponseAborted)
        self.assertIn('Expected \\r\\n after chunk data', out[2].reason_str)

    def test_uppercase_hex_chunk_size(self) -> None:
        """Test that uppercase hex chunk sizes work."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Use uppercase hex
        channel.feed_in(b'A\r\n' + b'x' * 10 + b'\r\n0\r\n\r\n')

        out = ibq.drain()

        self.assertEqual(len(out), 3)
        self.assertIsInstance(out[1], IoPipelineHttpResponseBodyData)
        self.assertEqual(out[1].data, b'x' * 10)
        self.assertIsInstance(out[2], IoPipelineHttpResponseEnd)

    def test_multiple_chunks(self) -> None:
        """Test multiple chunks in sequence."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        # Multiple small chunks
        chunks = [b'one', b'two', b'three', b'four', b'five']
        encoded = b''
        for chunk in chunks:
            encoded += f'{len(chunk):x}\r\n'.encode('ascii')
            encoded += chunk
            encoded += b'\r\n'
        encoded += b'0\r\n\r\n'

        channel.feed_in(encoded)

        out = ibq.drain()

        # head + 5 chunks + end
        self.assertEqual(len(out), 7)
        self.assertIsInstance(out[0], IoPipelineHttpResponseHead)

        for i, chunk in enumerate(chunks, 1):
            self.assertIsInstance(out[i], IoPipelineHttpResponseBodyData)
            self.assertEqual(out[i].data, chunk)

        self.assertIsInstance(out[6], IoPipelineHttpResponseEnd)

    def test_eof_after_complete_ok(self) -> None:
        """Test that EOF after complete chunked response is OK."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = (
            b'HTTP/1.1 200 OK\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )
        channel.feed_in(head)

        channel.feed_in(b'5\r\nhello\r\n0\r\n\r\n')
        channel.feed_in(IoPipelineMessages.FinalInput())

        out = ibq.drain()

        # Should complete without error
        self.assertEqual(len(out), 4)
        self.assertIsInstance(out[3], IoPipelineMessages.FinalInput)
