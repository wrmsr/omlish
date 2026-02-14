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
from ..responses import PipelineHttpResponseDecoder


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

    def on_consumed(self, cost: int) -> None:
        self.consumed.append(cost)

    def want_read(self) -> bool:
        return True

    def drain_outbound(self, max_cost: ta.Optional[int] = None) -> ta.List[ta.Any]:
        return []

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        # Just pass through - don't track or buffer
        ctx.feed_in(msg)


class TestPipelineHttpResponseDecoder(unittest.TestCase):
    def test_basic_response_head(self) -> None:
        """Test basic HTTP response head parsing."""

        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([decoder])

        response = b'HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n'
        channel.feed_in(response)

        out = channel.drain_out()
        self.assertEqual(len(out), 1)

        head = out[0]
        self.assertEqual(head.status, 200)
        self.assertEqual(head.reason, 'OK')
        self.assertEqual(head.headers.single.get('content-length'), '5')

    def test_response_with_body_in_same_chunk(self) -> None:
        """Test response head + body bytes received together."""

        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([decoder])

        response = b'HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello'
        channel.feed_in(response)

        out = channel.drain_out()
        self.assertEqual(len(out), 2)

        # First: head
        head = out[0]
        self.assertEqual(head.status, 200)

        # Second: body bytes
        body = out[1]
        self.assertEqual(ByteStreamBuffers.to_bytes(body), b'hello')

    def test_response_incremental_head(self) -> None:
        """Test response head received incrementally."""

        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([decoder])

        # Send head in parts
        channel.feed_in(b'HTTP/1.1 200 OK\r\n')
        out = channel.drain_out()
        self.assertEqual(len(out), 0)  # Not complete yet

        channel.feed_in(b'Content-Type: text/plain\r\n\r\n')
        out = channel.drain_out()
        self.assertEqual(len(out), 1)

        head = out[0]
        self.assertEqual(head.status, 200)
        self.assertEqual(head.headers.single.get('content-type'), 'text/plain')

    def test_flow_control_refund_with_preexisting_buffer(self) -> None:
        """
        Test flow control refund when buffer has preexisting data.

        This tests the bug fix: previously, the refund formula was:
            before - after + (i + 4)
        where 'before' was measured BEFORE writing new data.

        With a preexisting buffer, this would over-refund.

        Example:
        - Buffer starts with 50 bytes of partial head
        - Receive 50 more bytes completing the head (64 total consumed)
        - Old formula: 50 - 36 + 64 = 78 (wrong!)
        - New formula: 100 - 36 = 64 (correct)
        """

        flow = MockBytesFlowControl()
        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([flow, decoder])

        # Send partial head that doesn't complete
        partial = b'HTTP/1.1 200 OK\r\nContent-Length: 5\r\nX-Custom: '
        channel.feed_in(partial)

        # No head emitted yet, no refund
        out = channel.drain_out()
        self.assertEqual(len(out), 0)
        self.assertEqual(flow.consumed, [])

        # Now send the rest to complete the head
        rest = b'value\r\n\r\n'
        channel.feed_in(rest)

        out = channel.drain_out()
        self.assertEqual(len(out), 1)  # Head emitted

        # Verify refund is exactly the head size, not affected by buffer state
        total_head_size = len(partial) + len(rest)
        self.assertEqual(len(flow.consumed), 1)
        self.assertEqual(flow.consumed[0], total_head_size)

    def test_flow_control_refund_simple_case(self) -> None:
        """Test flow control refund in the simple case (empty buffer initially)."""

        flow = MockBytesFlowControl()
        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([flow, decoder])

        response = b'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n'
        channel.feed_in(response)

        out = channel.drain_out()
        self.assertEqual(len(out), 1)

        # Refund should equal the head size
        self.assertEqual(len(flow.consumed), 1)
        self.assertEqual(flow.consumed[0], len(response))

    def test_flow_control_refund_with_body_bytes(self) -> None:
        """Test that body bytes forwarded as bytes are NOT refunded by head decoder."""

        flow = MockBytesFlowControl()
        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([flow, decoder])

        head = b'HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\n'
        body = b'hellohello'
        response = head + body

        channel.feed_in(response)

        out = channel.drain_out()
        self.assertEqual(len(out), 2)  # Head + body bytes

        # Only the head should be refunded by the decoder
        # (body bytes are forwarded as bytes, downstream will refund them)
        self.assertEqual(len(flow.consumed), 1)
        self.assertEqual(flow.consumed[0], len(head))

    def test_eof_before_head_complete(self) -> None:
        """Test EOF arriving before head is complete raises ValueError."""

        decoder = PipelineHttpResponseDecoder()
        channel = PipelineChannel([decoder])

        # Send partial head
        channel.feed_in(b'HTTP/1.1 200 OK\r\n')

        # Send EOF
        channel.feed_eof()

        out = channel.drain_out()
        # Should get an error event
        self.assertTrue(any(isinstance(m, ChannelPipelineEvents.Error) for m in out))
