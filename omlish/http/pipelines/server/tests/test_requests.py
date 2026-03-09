# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import unittest

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.handlers.queues import InboundQueueIoPipelineHandler
from .....io.streams.utils import ByteStreamBuffers
from ...requests import FullIoPipelineHttpRequest
from ...requests import IoPipelineHttpRequestAborted
from ...requests import IoPipelineHttpRequestBodyData
from ...requests import IoPipelineHttpRequestEnd
from ...requests import IoPipelineHttpRequestHead
from ..requests import IoPipelineHttpRequestAggregatorDecoder
from ..requests import IoPipelineHttpRequestDecoder


class TestPipelineHttpRequestDecoder(unittest.TestCase):
    def test_basic_request_head(self) -> None:
        """Test basic HTTP request head parsing."""

        decoder = IoPipelineHttpRequestDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        request = b'GET /path HTTP/1.1\r\nHost: example.com\r\n\r\n'
        channel.feed_in(request)

        head, end = ibq.drain()
        self.assertIsInstance(head, IoPipelineHttpRequestHead)
        self.assertEqual(head.method, 'GET')
        self.assertEqual(head.target, '/path')
        self.assertEqual(head.headers.single.get('host'), 'example.com')
        self.assertIsInstance(end, IoPipelineHttpRequestEnd)

    def test_request_with_body_in_same_chunk(self) -> None:
        """Test request head + body bytes received together."""

        decoder = IoPipelineHttpRequestDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 4\r\n\r\ntest'
        channel.feed_in(request)

        head, body, end = ibq.drain()

        # First: head
        self.assertEqual(head.method, 'POST')
        self.assertEqual(head.target, '/api')

        # Second: body bytes (forwarded)
        self.assertIsInstance(body, IoPipelineHttpRequestBodyData)
        self.assertEqual(ByteStreamBuffers.to_bytes(body.data), b'test')

        self.assertIsInstance(end, IoPipelineHttpRequestEnd)

    def test_eof_before_head_complete(self) -> None:
        """Test EOF before head complete raises error."""

        decoder = IoPipelineHttpRequestDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        channel.feed_in(b'GET /path HTTP/1.1\r\n')
        channel.feed_final_input()

        aborted, eof = ibq.drain()
        self.assertIsInstance(aborted, IoPipelineHttpRequestAborted)
        self.assertIsInstance(eof, IoPipelineMessages.FinalInput)


class TestPipelineHttpRequestAggregatorDecoder(unittest.TestCase):
    def test_request_with_no_body(self) -> None:
        """Test request with no Content-Length."""

        head_decoder = IoPipelineHttpRequestDecoder()
        body_agg = IoPipelineHttpRequestAggregatorDecoder()
        channel = IoPipeline.new([
            head_decoder,
            body_agg,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        request = b'GET / HTTP/1.1\r\nHost: test\r\n\r\n'
        channel.feed_in(request)

        [req] = ibq.drain()
        self.assertIsInstance(req, FullIoPipelineHttpRequest)
        self.assertEqual(req.head.method, 'GET')
        self.assertEqual(req.body, b'')

    def test_request_with_body_same_chunk(self) -> None:
        """Test request with body in same chunk as head."""

        head_decoder = IoPipelineHttpRequestDecoder()
        body_agg = IoPipelineHttpRequestAggregatorDecoder()
        channel = IoPipeline.new([
            head_decoder,
            body_agg,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 11\r\n\r\nhello world'
        channel.feed_in(request)

        out = ibq.drain()
        self.assertEqual(len(out), 1)

        req = out[0]
        self.assertIsInstance(req, FullIoPipelineHttpRequest)
        self.assertEqual(req.head.method, 'POST')
        self.assertEqual(req.body, b'hello world')

    def test_request_with_body_multiple_chunks(self) -> None:
        """Test request body received in multiple chunks."""

        head_decoder = IoPipelineHttpRequestDecoder()
        body_agg = IoPipelineHttpRequestAggregatorDecoder()
        channel = IoPipeline.new([
            head_decoder,
            body_agg,
            ibq := InboundQueueIoPipelineHandler(),
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

        head_decoder = IoPipelineHttpRequestDecoder()
        body_agg = IoPipelineHttpRequestAggregatorDecoder()
        channel = IoPipeline.new([
            head_decoder,
            body_agg,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        head = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 10\r\n\r\n'
        channel.feed_in(head)
        self.assertEqual(ibq.drain(), [])

        # Send partial body then EOF
        channel.feed_in(b'hello')
        channel.feed_final_input()

        out = ibq.drain()
        aborted = out[-2]  # FIXME: duplicate aborted from decoder + aggregator
        eof = out[-1]
        self.assertIsInstance(aborted, IoPipelineHttpRequestAborted)
        self.assertIsInstance(eof, IoPipelineMessages.FinalInput)


class TestPipelineHttpRequestObjectDecoder(unittest.TestCase):
    def test_basic_request_head(self) -> None:
        decoder = IoPipelineHttpRequestDecoder()
        channel = IoPipeline(IoPipeline.Spec([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ]).update_config(raise_immediately=True))

        request = b'GET /path HTTP/1.1\r\nHost: example.com\r\n\r\n'
        channel.feed_in(request)

        head, end = ibq.drain()
        self.assertIsInstance(head, IoPipelineHttpRequestHead)
        self.assertEqual(head.method, 'GET')
        self.assertEqual(head.target, '/path')
        self.assertEqual(head.headers.single.get('host'), 'example.com')
        self.assertIsInstance(end, IoPipelineHttpRequestEnd)

    def test_request_with_body_in_same_chunk(self) -> None:
        """Test request head + body bytes received together."""

        decoder = IoPipelineHttpRequestDecoder()
        channel = IoPipeline(IoPipeline.Spec([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ]).update_config(raise_immediately=True))

        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 4\r\n\r\ntest'
        channel.feed_in(request)

        out = ibq.drain()
        self.assertEqual(len(out), 3)

        # First: head
        head, body, end = out
        self.assertEqual(head.method, 'POST')
        self.assertEqual(head.target, '/api')

        # Second: body bytes (forwarded)
        self.assertIsInstance(body, IoPipelineHttpRequestBodyData)
        self.assertEqual(ByteStreamBuffers.to_bytes(body.data), b'test')

        # Second: body bytes (forwarded)
        self.assertIsInstance(end, IoPipelineHttpRequestEnd)

    def test_chunked(self):
        head_b = (
            b'POST /api HTTP/1.1\r\n'
            b'Host: test\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n'
        )

        body_b = (
            b'a\r\n' + b'0123456789' + b'\r\n' +
            b'10\r\n' + b'a' * 16 + b'\r\n' +
            b'64\r\n' + b'b' * 100 + b'\r\n' +
            b'0\r\n\r\n'
        )

        decoder = IoPipelineHttpRequestDecoder()
        channel = IoPipeline(IoPipeline.Spec([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ]).update_config(raise_immediately=True))

        channel.feed_in(head_b + body_b)

        out = ibq.drain()

        self.assertEqual(len(out), 5)  # head + 3 chunks + end
        self.assertIsInstance(out[1], IoPipelineHttpRequestBodyData)
        self.assertEqual(out[1].data, b'0123456789')
        self.assertIsInstance(out[2], IoPipelineHttpRequestBodyData)
        self.assertEqual(out[2].data, b'a' * 16)
        self.assertIsInstance(out[3], IoPipelineHttpRequestBodyData)
        self.assertEqual(out[3].data, b'b' * 100)
        self.assertIsInstance(out[4], IoPipelineHttpRequestEnd)
