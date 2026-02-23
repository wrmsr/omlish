# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import unittest

from omlish.io.streams.utils import ByteStreamBuffers

from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ..responses import PipelineHttpResponseAborted
from ..responses import PipelineHttpResponseDecoder
from ....handlers.queues import InboundQueueChannelPipelineHandler


class TestPipelineHttpResponseDecoder(unittest.TestCase):
    def test_basic_response_head(self) -> None:
        """Test basic HTTP response head parsing."""

        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([
            decoder,
            ibq := InboundQueueChannelPipelineHandler(),
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

        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([
            decoder,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        response = b'HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello'
        channel.feed_in(response)

        out = ibq.drain()
        self.assertEqual(len(out), 2)

        # First: head
        head = out[0]
        self.assertEqual(head.status, 200)

        # Second: body bytes
        body = out[1]
        self.assertEqual(ByteStreamBuffers.any_to_bytes(body), b'hello')

    def test_response_incremental_head(self) -> None:
        """Test response head received incrementally."""

        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([
            decoder,
            ibq := InboundQueueChannelPipelineHandler(),
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

        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([
            decoder,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        # Send partial head
        channel.feed_in(b'HTTP/1.1 200 OK\r\n')

        # Send EOF
        channel.feed_final_input()

        out = ibq.drain()

        # Should get an aborted message
        aborted, eof = out
        self.assertIsInstance(aborted, PipelineHttpResponseAborted)
        self.assertIsInstance(eof, ChannelPipelineMessages.FinalInput)
