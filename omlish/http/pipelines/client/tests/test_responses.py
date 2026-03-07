# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import unittest

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.handlers.queues import InboundQueueIoPipelineHandler
from .....io.streams.utils import ByteStreamBuffers
from ...responses import IoPipelineHttpResponseAborted
from ...responses import IoPipelineHttpResponseContentChunkData
from ...responses import IoPipelineHttpResponseEnd
from ..responses import IoPipelineHttpResponseDecoder


class TestPipelineHttpResponseDecoder(unittest.TestCase):
    def test_basic_response_head(self) -> None:
        """Test basic HTTP response head parsing."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        response = b'HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n'
        channel.feed_in(response)

        out = ibq.drain()
        self.assertEqual(len(out), 1)

        head = out[0]
        self.assertEqual(head.status, 200)
        self.assertEqual(head.reason, 'OK')
        self.assertEqual(head.headers.single.get('content-length'), '5')

    def test_response_with_body_in_same_chunk(self) -> None:
        """Test response head + body bytes received together."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        response = b'HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello'
        channel.feed_in(response)

        head, body, end = ibq.drain()

        # First: head
        self.assertEqual(head.status, 200)

        # Second: body bytes
        self.assertIsInstance(body, IoPipelineHttpResponseContentChunkData)
        self.assertEqual(ByteStreamBuffers.to_bytes(body.data), b'hello')

        self.assertIsInstance(end, IoPipelineHttpResponseEnd)

    def test_response_incremental_head(self) -> None:
        """Test response head received incrementally."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        # Send head in parts
        channel.feed_in(b'HTTP/1.1 200 OK\r\n')
        out = ibq.drain()
        self.assertEqual(len(out), 0)  # Not complete yet

        channel.feed_in(b'Content-Type: text/plain\r\n\r\n')
        out = ibq.drain()
        self.assertEqual(len(out), 1)

        head = out[0]
        self.assertEqual(head.status, 200)
        self.assertEqual(head.headers.single.get('content-type'), 'text/plain')

    def test_eof_before_head_complete(self) -> None:
        """Test EOF arriving before head is complete raises ValueError."""

        decoder = IoPipelineHttpResponseDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        # Send partial head
        channel.feed_in(b'HTTP/1.1 200 OK\r\n')

        # Send EOF
        channel.feed_final_input()

        out = ibq.drain()

        # Should get an aborted message
        aborted, eof = out
        self.assertIsInstance(aborted, IoPipelineHttpResponseAborted)
        self.assertIsInstance(eof, IoPipelineMessages.FinalInput)
