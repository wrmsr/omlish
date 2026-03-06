# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import unittest
import zlib

from omlish.http.headers import HttpHeaders
from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....handlers.queues import InboundQueueChannelPipelineHandler
from ...responses import PipelineHttpResponseHead
from ..responses import PipelineHttpCompressionDecodingConfig
from ..responses import PipelineHttpResponseAborted
from ..responses import PipelineHttpResponseConditionalGzipDecoder
from ..responses import PipelineHttpResponseHeadDecoder


class TestPipelineHttpResponseDecoder(unittest.TestCase):
    def test_basic_response_head(self) -> None:
        """Test basic HTTP response head parsing."""

        decoder = PipelineHttpResponseHeadDecoder()
        channel = PipelineChannel.new([
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

        decoder = PipelineHttpResponseHeadDecoder()
        channel = PipelineChannel.new([
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

        decoder = PipelineHttpResponseHeadDecoder()
        channel = PipelineChannel.new([
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

        decoder = PipelineHttpResponseHeadDecoder()
        channel = PipelineChannel.new([
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


class TestGzipDecompressorFlow(unittest.TestCase):
    config = PipelineHttpCompressionDecodingConfig(
        max_steps_per_call=2,      # Very low for testing
        max_decomp_chunk=10,       # Tiny chunks to force multiple steps
        max_out_pending=100,
        max_expansion_ratio=1000,   # High for zip bomb testing
    )

    # Enable Gzip
    head = PipelineHttpResponseHead(
        status=200,
        reason='OK',
        headers=HttpHeaders({'content-encoding': 'gzip'}),
    )

    def test_deferral(self):
        # Create some gzip data
        compressor = zlib.compressobj(wbits=16 + zlib.MAX_WBITS)
        # Create enough data to exceed 2 steps (2 * 10 bytes)
        raw_data = b'This is a reasonably long string that should exceed the tiny chunk limit.'
        data = compressor.compress(raw_data) + compressor.flush()

        handler = PipelineHttpResponseConditionalGzipDecoder(config=self.config)

        channel = PipelineChannel.new(
            [
                handler,
                ibq := InboundQueueChannelPipelineHandler(),
            ],
        )

        # 1. Feed data and FinalInput
        channel.feed_in(self.head)
        assert channel.output.drain() == []
        assert ibq.drain() == [self.head]

        channel.feed_in(data)
        # Should have deferred because max_steps is 2 (20 bytes out max)
        dfl = check.isinstance(check.single(channel.output.drain()), ChannelPipelineMessages.Defer)
        # Verify FinalInput is pinned and NOT yet fed inbound
        self.assertIsNone(dfl.pinned)

        # 2. Run the deferred tasks until completion
        count = 0
        channel.run_deferred(dfl)
        while (out := channel.output.poll()) is not None:
            count += 1
            if count > 100:
                self.fail('Infinite defer loop')
            dfl = check.isinstance(out, ChannelPipelineMessages.Defer)
            channel.run_deferred(dfl)

        fi = ChannelPipelineMessages.FinalInput()
        channel.feed_in(fi)
        assert channel.output.drain() == []
        [*out_data, out_fi] = ibq.drain()

        # 3. Final Verification
        full_output = b''.join(m for m in out_data)
        self.assertEqual(full_output, raw_data)
        self.assertIs(fi, out_fi)

    def test_zip_bomb_prevention(self):
        """Test that budget checks trigger even during deferred steps."""

        config = dc.replace(self.config, max_expansion_ratio=2)
        handler = PipelineHttpResponseConditionalGzipDecoder(config=config)

        # 10 bytes compressed -> 1000 bytes uncompressed (ratio 100)
        compressor = zlib.compressobj(wbits=16 + zlib.MAX_WBITS)
        bomb_data = compressor.compress(b'A' * 1000) + compressor.flush()

        channel = PipelineChannel.new(
            [
                handler,
                ibq := InboundQueueChannelPipelineHandler(),  # noqa
            ],
        )
        channel.feed_in(self.head)

        # Feeding this should eventually raise ValueError due to expansion ratio
        channel.feed_in(bomb_data)
        count = 0
        while (out := channel.output.poll()) is not None:
            count += 1
            if count > 100:
                self.fail('Infinite defer loop')
            dfl = check.isinstance(out, ChannelPipelineMessages.Defer)
            channel.run_deferred(dfl)

        [out_head, *out_data, out_err] = ibq.drain()
        self.assertIs(self.head, out_head)
        err = check.isinstance(out_err, ChannelPipelineMessages.Error)
        self.assertIsInstance(err.exc, ValueError)
        self.assertIn('expansion ratio exceeds limit', repr(err.exc))

    # def test_manual_read_backpressure_with_defer(self):
    #     """Test that manual read (auto_read=False) correctly stalls the defer loop."""
    #
    #     self.ctx.services[ChannelPipelineFlow] = StubChannelPipelineFlow(auto_read=False)
    #
    #     compressor = zlib.compressobj(wbits=16+zlib.MAX_WBITS)
    #     data = compressor.compress(b"Some data that will be buffered") + compressor.flush()
    #
    #     # 1. Feed data - should decompress one chunk and stop because _read_requested is False
    #     self.handler.inbound(self.ctx, data)
    #
    #     # No data should have been fed in yet because no ReadyForInput was received
    #     self.assertEqual(len([m for m in self.ctx.inbound_results if isinstance(m, bytes)]), 0)
    #
    #     # 2. Send ReadyForInput
    #     self.handler.outbound(self.ctx, ChannelPipelineFlowMessages.ReadyForInput())
    #
    #     # Now one chunk should be present
    #     self.assertGreater(len(self.ctx.inbound_results), 0)
