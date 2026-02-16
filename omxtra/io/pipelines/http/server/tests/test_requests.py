# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta
import unittest

from omlish.io.streams.utils import ByteStreamBuffers

from ....core import BytesChannelPipelineFlowControl
from ....core import ChannelPipelineEvents
from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import PipelineChannel
from ..requests import FullPipelineHttpRequest
from ..requests import PipelineHttpRequestBodyAggregator
from ..requests import PipelineHttpRequestHead
from ..requests import PipelineHttpRequestHeadDecoder


class MockBytesFlowControl(BytesChannelPipelineFlowControl, ChannelPipelineHandler):
    """
    Mock flow control that only tracks on_consumed calls.
    Does NOT intercept or buffer messages - just passes them through.
    """

    def __init__(self) -> None:
        super().__init__()

        self.consumed: ta.List[int] = []

    def get_cost(self, msg: ta.Any) -> ta.Optional[int]:
        # Return None so we don't interfere with message flow
        return None

    def on_consumed(self, handler: ChannelPipelineHandler, cost: int) -> None:
        self.consumed.append(cost)

    def want_read(self) -> bool:
        return True

    def drain_outbound(self, max_cost: ta.Optional[int] = None) -> ta.List[ta.Any]:
        return []

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        # Just pass through - don't track or buffer
        ctx.feed_in(msg)


class TestPipelineHttpRequestHeadDecoder(unittest.TestCase):
    def test_basic_request_head(self) -> None:
        """Test basic HTTP request head parsing."""

        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel([decoder])

        request = b'GET /path HTTP/1.1\r\nHost: example.com\r\n\r\n'
        channel.feed_in(request)

        out = channel.drain()
        self.assertEqual(len(out), 1)

        head = out[0]
        self.assertIsInstance(head, PipelineHttpRequestHead)
        self.assertEqual(head.method, 'GET')
        self.assertEqual(head.target, '/path')
        self.assertEqual(head.headers.single.get('host'), 'example.com')

    def test_request_with_body_in_same_chunk(self) -> None:
        """Test request head + body bytes received together."""

        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel([decoder])

        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 4\r\n\r\ntest'
        channel.feed_in(request)

        out = channel.drain()
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
        channel = PipelineChannel([decoder])

        # Send head
        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 10\r\n\r\n'
        channel.feed_in(request)

        out = channel.drain()
        self.assertEqual(len(out), 1)

        # Send body in chunks - should all pass through
        channel.feed_in(b'hello')
        channel.feed_in(b'world')

        out = channel.drain()
        self.assertEqual(len(out), 2)
        self.assertEqual(ByteStreamBuffers.any_to_bytes(out[0]), b'hello')
        self.assertEqual(ByteStreamBuffers.any_to_bytes(out[1]), b'world')

    def test_flow_control_refund_with_preexisting_buffer(self) -> None:
        """
        Test flow control refund when buffer has preexisting data.

        This tests the bug fix where the old formula:
            before - after + (i + 4)
        would over-refund when 'before' was measured before writing.

        Example:
        - Buffer has 50 bytes of incomplete head
        - Receive 50 more bytes to complete 64-byte head
        - Old: 50 - 36 + 64 = 78 (wrong!)
        - New: 100 - 36 = 64 (correct)
        """

        flow = MockBytesFlowControl()
        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel([flow, decoder])

        # Send partial head
        partial = b'GET /path HTTP/1.1\r\nHost: example.com\r\nX-Custom: '
        channel.feed_in(partial)

        out = channel.drain()
        self.assertEqual(len(out), 0)
        self.assertEqual(flow.consumed, [])

        # Complete the head
        rest = b'value\r\n\r\n'
        channel.feed_in(rest)

        out = channel.drain()
        self.assertEqual(len(out), 1)

        # Refund should equal total head size
        total_head_size = len(partial) + len(rest)
        self.assertEqual(len(flow.consumed), 1)
        self.assertEqual(flow.consumed[0], total_head_size)

    def test_flow_control_refund_simple_case(self) -> None:
        """Test flow control refund in simple case (empty buffer initially)."""

        flow = MockBytesFlowControl()
        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel([flow, decoder])

        request = b'GET / HTTP/1.1\r\nHost: test\r\n\r\n'
        channel.feed_in(request)

        out = channel.drain()
        self.assertEqual(len(out), 1)

        self.assertEqual(len(flow.consumed), 1)
        self.assertEqual(flow.consumed[0], len(request))

    def test_flow_control_no_refund_for_forwarded_body_bytes(self) -> None:
        """Test that body bytes forwarded are NOT refunded by head decoder."""

        flow = MockBytesFlowControl()
        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel([flow, decoder])

        head = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 5\r\n\r\n'
        body = b'hello'
        request = head + body

        channel.feed_in(request)

        out = channel.drain()
        self.assertEqual(len(out), 2)  # head + body bytes

        # Only head should be refunded
        self.assertEqual(len(flow.consumed), 1)
        self.assertEqual(flow.consumed[0], len(head))

    def test_eof_before_head_complete(self) -> None:
        """Test EOF before head complete raises error."""

        decoder = PipelineHttpRequestHeadDecoder()
        channel = PipelineChannel([decoder])

        channel.feed_in(b'GET /path HTTP/1.1\r\n')
        channel.feed_eof()

        out = channel.drain()
        self.assertTrue(any(isinstance(m, ChannelPipelineEvents.Error) for m in out))


class TestPipelineHttpRequestBodyAggregator(unittest.TestCase):
    def test_request_with_no_body(self) -> None:
        """Test request with no Content-Length."""

        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel([head_decoder, body_agg])

        request = b'GET / HTTP/1.1\r\nHost: test\r\n\r\n'
        channel.feed_in(request)

        out = channel.drain()
        self.assertEqual(len(out), 1)

        req = out[0]
        self.assertIsInstance(req, FullPipelineHttpRequest)
        self.assertEqual(req.head.method, 'GET')
        self.assertEqual(req.body, b'')

    def test_request_with_body_same_chunk(self) -> None:
        """Test request with body in same chunk as head."""

        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel([head_decoder, body_agg])

        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 11\r\n\r\nhello world'
        channel.feed_in(request)

        out = channel.drain()
        self.assertEqual(len(out), 1)

        req = out[0]
        self.assertIsInstance(req, FullPipelineHttpRequest)
        self.assertEqual(req.head.method, 'POST')
        self.assertEqual(req.body, b'hello world')

    def test_request_with_body_multiple_chunks(self) -> None:
        """Test request body received in multiple chunks."""

        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel([head_decoder, body_agg])

        # Send head
        head = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 10\r\n\r\n'
        channel.feed_in(head)

        out = channel.drain()
        self.assertEqual(len(out), 0)  # Waiting for body

        # Send body in parts
        channel.feed_in(b'hello')
        out = channel.drain()
        self.assertEqual(len(out), 0)  # Still waiting

        channel.feed_in(b'world')
        out = channel.drain()
        self.assertEqual(len(out), 1)  # Complete!

        req = out[0]
        self.assertEqual(req.body, b'helloworld')

    def test_flow_control_refund_with_preexisting_buffer(self) -> None:
        """
        Test flow control refund when body buffer has preexisting data.

        Bug fix test: old formula was:
            before - after + self._want
        where 'before' was measured before writing.

        Example:
        - Head parsed, want 10 bytes
        - Buffer gets 5 bytes
        - Buffer gets 5 more bytes (now complete)
        - Old: 5 - 0 + 10 = 15 (wrong!)
        - New: 10 - 0 = 10 (correct)
        """

        flow = MockBytesFlowControl()
        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel([flow, head_decoder, body_agg])

        # Send head
        head = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 10\r\n\r\n'
        channel.feed_in(head)
        channel.drain()

        # Clear previous consumption tracking
        flow.consumed.clear()

        # Send body in two parts
        channel.feed_in(b'hello')
        channel.drain()
        self.assertEqual(flow.consumed, [])  # No refund yet, body incomplete

        channel.feed_in(b'world')
        out = channel.drain()
        self.assertEqual(len(out), 1)

        # Should refund exactly 10 bytes (the body consumed)
        self.assertEqual(len(flow.consumed), 1)
        self.assertEqual(flow.consumed[0], 10)

    def test_flow_control_refund_simple_case(self) -> None:
        """Test flow control refund in simple case."""

        flow = MockBytesFlowControl()
        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel([flow, head_decoder, body_agg])

        request = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 4\r\n\r\ntest'
        channel.feed_in(request)

        out = channel.drain()
        self.assertEqual(len(out), 1)

        # Should have two refunds: head (from head decoder) + body (from aggregator)
        self.assertEqual(len(flow.consumed), 2)
        head_size = len(b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 4\r\n\r\n')
        self.assertEqual(flow.consumed[0], head_size)  # head
        self.assertEqual(flow.consumed[1], 4)  # body

    def test_eof_before_body_complete(self) -> None:
        """Test EOF before body complete raises error."""

        head_decoder = PipelineHttpRequestHeadDecoder()
        body_agg = PipelineHttpRequestBodyAggregator()
        channel = PipelineChannel([head_decoder, body_agg])

        head = b'POST /api HTTP/1.1\r\nHost: test\r\nContent-Length: 10\r\n\r\n'
        channel.feed_in(head)
        channel.drain()

        # Send partial body then EOF
        channel.feed_in(b'hello')
        channel.feed_eof()

        out = channel.drain()
        self.assertTrue(any(isinstance(m, ChannelPipelineEvents.Error) for m in out))
