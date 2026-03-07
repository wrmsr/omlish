# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import unittest
import zlib

from .....io.pipelines.core import ChannelPipelineMessages
from .....io.pipelines.core import PipelineChannel
from .....io.pipelines.handlers.queues import InboundQueueChannelPipelineHandler
from .....lite.check import check
from ....headers import HttpHeaders
from ...decompressors import PipelineHttpDecompressionConfig
from ...responses import PipelineHttpResponseContentChunkData
from ...responses import PipelineHttpResponseEnd
from ...responses import PipelineHttpResponseHead
from ..responses import PipelineHttpResponseDecompressor


class TestGzipDecompressorFlow(unittest.TestCase):
    config = PipelineHttpDecompressionConfig(
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

        handler = PipelineHttpResponseDecompressor(config=self.config)

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

        channel.feed_in(PipelineHttpResponseContentChunkData(data))
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

        fi = PipelineHttpResponseEnd()
        channel.feed_in(fi)
        assert channel.output.drain() == []
        [*out_data, out_fi] = ibq.drain()

        # 3. Final Verification
        full_output = b''.join(check.isinstance(m, PipelineHttpResponseContentChunkData).data for m in out_data)
        self.assertEqual(full_output, raw_data)
        self.assertIs(fi, out_fi)

    def test_zip_bomb_prevention(self):
        """Test that budget checks trigger even during deferred steps."""

        config = dc.replace(self.config, max_expansion_ratio=2)
        handler = PipelineHttpResponseDecompressor(config=config)

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
        channel.feed_in(PipelineHttpResponseContentChunkData(bomb_data))
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
