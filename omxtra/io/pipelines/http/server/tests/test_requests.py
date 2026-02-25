# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import unittest

from omlish.io.streams.utils import ByteStreamBuffers

from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....handlers.queues import InboundQueueChannelPipelineHandler
from ..requests import FullPipelineHttpRequest
from ..requests import PipelineHttpRequestAborted
from ..requests import PipelineHttpRequestBodyAggregator
from ..requests import PipelineHttpRequestHead
from ..requests import PipelineHttpRequestHeadDecoder


class TestPipelineHttpRequestHeadDecoder(unittest.TestCase):
    def test_basic_request_head(self) -> None:
        """Test basic HTTP request head parsing."""

        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel.new([
            decoder,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        request = b'GET /path HTTP/1.1\r\nHost: example.com\r\n\r\n'
        channel.feed_in(request)

        out = ibq.drain()
        self.assertEqual(len(out), 1)

        head = out[0]
        self.assertIsInstance(head, PipelineHttpRequestHead)
        self.assertEqual(head.method, 'GET')
        self.assertEqual(head.target, '/path')
        self.assertEqual(head.headers.single.get('host'), 'example.com')

    def test_request_with_body_in_same_chunk(self) -> None:
        """Test request head + body bytes received together."""

        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel.new([
            decoder,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 4\r\n\r\ntest'
        channel.feed_in(request)

        out = ibq.drain()
        self.assertEqual(len(out), 2)

        # First: head
        head = out[0]
        self.assertEqual(head.method, 'POST')
        self.assertEqual(head.target, '/api')

        # Second: body bytes (forwarded)
        body = out[1]
        self.assertEqual(ByteStreamBuffers.any_to_bytes(body), b'test')

    def test_body_passthrough_mode(self) -> None:
        """Test that after head parsed, subsequent bytes pass through."""

        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel.new([
            decoder,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        # Send head
        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 10\r\n\r\n'
        channel.feed_in(request)

        out = ibq.drain()
        self.assertEqual(len(out), 1)

        # Send body in chunks - should all pass through
        channel.feed_in(b'hello')
        channel.feed_in(b'world')

        out = ibq.drain()
        self.assertEqual(len(out), 2)
        self.assertEqual(ByteStreamBuffers.any_to_bytes(out[0]), b'hello')
        self.assertEqual(ByteStreamBuffers.any_to_bytes(out[1]), b'world')

    def test_eof_before_head_complete(self) -> None:
        """Test EOF before head complete raises error."""

        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel.new([
            decoder,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        channel.feed_in(b'GET /path HTTP/1.1\r\n')
        channel.feed_final_input()

        aborted, eof = ibq.drain()
        self.assertIsInstance(aborted, PipelineHttpRequestAborted)
        self.assertIsInstance(eof, ChannelPipelineMessages.FinalInput)


class TestPipelineHttpRequestBodyAggregator(unittest.TestCase):
    def test_request_with_no_body(self) -> None:
        """Test request with no Content-Length."""

        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel.new([
            head_decoder,
            body_agg,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        request = b'GET / HTTP/1.1\r\nHost: test\r\n\r\n'
        channel.feed_in(request)

        out = ibq.drain()
        self.assertEqual(len(out), 1)

        req = out[0]
        self.assertIsInstance(req, FullPipelineHttpRequest)
        self.assertEqual(req.head.method, 'GET')
        self.assertEqual(req.body, b'')

    def test_request_with_body_same_chunk(self) -> None:
        """Test request with body in same chunk as head."""

        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel.new([
            head_decoder,
            body_agg,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 11\r\n\r\nhello world'
        channel.feed_in(request)

        out = ibq.drain()
        self.assertEqual(len(out), 1)

        req = out[0]
        self.assertIsInstance(req, FullPipelineHttpRequest)
        self.assertEqual(req.head.method, 'POST')
        self.assertEqual(req.body, b'hello world')

    def test_request_with_body_multiple_chunks(self) -> None:
        """Test request body received in multiple chunks."""

        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel.new([
            head_decoder,
            body_agg,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        # Send head
        head = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 10\r\n\r\n'
        channel.feed_in(head)

        out = ibq.drain()
        self.assertEqual(len(out), 0)  # Waiting for body

        # Send body in parts
        channel.feed_in(b'hello')
        out = ibq.drain()
        self.assertEqual(len(out), 0)  # Still waiting

        channel.feed_in(b'world')
        out = ibq.drain()
        self.assertEqual(len(out), 1)  # Complete!

        req = out[0]
        self.assertEqual(req.body, b'helloworld')

    def test_eof_before_body_complete(self) -> None:
        """Test EOF before body complete raises error."""

        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel.new([
            head_decoder,
            body_agg,
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        head = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 10\r\n\r\n'
        channel.feed_in(head)
        ibq.drain()

        # Send partial body then EOF
        channel.feed_in(b'hello')
        channel.feed_final_input()

        aborted, eof = ibq.drain()
        self.assertIsInstance(aborted, PipelineHttpRequestAborted)
        self.assertIsInstance(eof, ChannelPipelineMessages.FinalInput)
