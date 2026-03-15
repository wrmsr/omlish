# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import unittest
import zlib

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.handlers.queues import InboundQueueIoPipelineHandler
from .....lite.check import check
from ....headers import HttpHeaders
from ...compression.decompressors import IoPipelineHttpDecompressionConfig
from ...responses import IoPipelineHttpResponseBodyData
from ...responses import IoPipelineHttpResponseEnd
from ...responses import IoPipelineHttpResponseHead
from ..responses import IoPipelineHttpResponseDecompressor


class TestGzipDecompressorSimple(unittest.TestCase):
    """Simple decompression tests without flow control complexity."""

    def test_passthrough_no_encoding(self):
        """Test that data passes through unchanged when no content-encoding is present."""
        handler = IoPipelineHttpResponseDecompressor()

        channel = IoPipeline.new([
            handler,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        # Head without content-encoding
        head = IoPipelineHttpResponseHead(
            status=200,
            reason='OK',
            headers=HttpHeaders({}),
        )

        # Feed messages
        channel.feed_in(head)
        channel.feed_in(IoPipelineHttpResponseBodyData(b'Hello, World!'))
        channel.feed_in(IoPipelineHttpResponseEnd())

        # Verify passthrough
        results = ibq.drain()
        self.assertEqual(len(results), 3)
        self.assertIs(results[0], head)
        self.assertEqual(check.isinstance(results[1], IoPipelineHttpResponseBodyData).data, b'Hello, World!')
        self.assertIsInstance(results[2], IoPipelineHttpResponseEnd)

    def test_simple_gzip_decompression(self):
        """Test basic gzip decompression with default config."""
        handler = IoPipelineHttpResponseDecompressor()

        channel = IoPipeline.new([
            handler,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        # Create gzipped data
        raw_data = b'Hello, World!'
        compressor = zlib.compressobj(wbits=16 + zlib.MAX_WBITS)
        compressed_data = compressor.compress(raw_data) + compressor.flush()

        # Head with gzip encoding
        head = IoPipelineHttpResponseHead(
            status=200,
            reason='OK',
            headers=HttpHeaders({'content-encoding': 'gzip'}),
        )

        # Feed messages
        channel.feed_in(head)
        channel.feed_in(IoPipelineHttpResponseBodyData(compressed_data))
        channel.feed_in(IoPipelineHttpResponseEnd())

        # Verify decompression
        results = ibq.drain()
        self.assertEqual(len(results), 3)
        self.assertIs(results[0], head)
        self.assertEqual(check.isinstance(results[1], IoPipelineHttpResponseBodyData).data, raw_data)
        self.assertIsInstance(results[2], IoPipelineHttpResponseEnd)

    def test_gzip_multiple_chunks(self):
        """Test gzip decompression with multiple body data chunks."""
        handler = IoPipelineHttpResponseDecompressor()

        channel = IoPipeline.new([
            handler,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        # Create gzipped data
        raw_data = b'This is a longer message that will be split into chunks during compression.'
        compressor = zlib.compressobj(wbits=16 + zlib.MAX_WBITS)
        compressed_data = compressor.compress(raw_data) + compressor.flush()

        # Split compressed data into chunks
        chunk_size = len(compressed_data) // 3
        chunk1 = compressed_data[:chunk_size]
        chunk2 = compressed_data[chunk_size:2 * chunk_size]
        chunk3 = compressed_data[2 * chunk_size:]

        # Head with gzip encoding
        head = IoPipelineHttpResponseHead(
            status=200,
            reason='OK',
            headers=HttpHeaders({'content-encoding': 'gzip'}),
        )

        # Feed messages
        channel.feed_in(head)
        channel.feed_in(IoPipelineHttpResponseBodyData(chunk1))
        channel.feed_in(IoPipelineHttpResponseBodyData(chunk2))
        channel.feed_in(IoPipelineHttpResponseBodyData(chunk3))
        channel.feed_in(IoPipelineHttpResponseEnd())

        # Verify decompression - collect all body data
        results = ibq.drain()
        self.assertIs(results[0], head)

        body_data_msgs = [m for m in results[1:-1] if isinstance(m, IoPipelineHttpResponseBodyData)]
        decompressed = b''.join(m.data for m in body_data_msgs)

        self.assertEqual(decompressed, raw_data)
        self.assertIsInstance(results[-1], IoPipelineHttpResponseEnd)


class TestGzipDecompressorFlow(unittest.TestCase):
    config = IoPipelineHttpDecompressionConfig(
        max_steps_per_call=2,      # Very low for testing
        max_decomp_chunk=10,       # Tiny chunks to force multiple steps
        max_out_pending=100,
        max_expansion_ratio=1000,   # High for zip bomb testing
    )

    # Enable Gzip
    head = IoPipelineHttpResponseHead(
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

        handler = IoPipelineHttpResponseDecompressor(config=self.config)

        channel = IoPipeline.new(
            [
                handler,
                ibq := InboundQueueIoPipelineHandler(),
            ],
        )

        # 1. Feed data and FinalInput
        channel.feed_in(self.head)
        assert channel.output.drain() == []
        assert ibq.drain() == [self.head]

        channel.feed_in(IoPipelineHttpResponseBodyData(data))
        # Should have deferred because max_steps is 2 (20 bytes out max)
        dfl = check.isinstance(check.single(channel.output.drain()), IoPipelineMessages.Defer)
        # Verify FinalInput is pinned and NOT yet fed inbound
        self.assertIsNone(dfl.pinned)

        # 2. Run the deferred tasks until completion
        count = 0
        channel.run_deferred(dfl)
        while (out := channel.output.poll()) is not None:
            count += 1
            if count > 100:
                self.fail('Infinite defer loop')
            dfl = check.isinstance(out, IoPipelineMessages.Defer)
            channel.run_deferred(dfl)

        fi = IoPipelineHttpResponseEnd()
        channel.feed_in(fi)
        assert channel.output.drain() == []
        [*out_data, out_fi] = ibq.drain()

        # 3. Final Verification
        full_output = b''.join(check.isinstance(m, IoPipelineHttpResponseBodyData).data for m in out_data)
        self.assertEqual(full_output, raw_data)
        self.assertIs(fi, out_fi)

    def test_zip_bomb_prevention(self):
        """Test that budget checks trigger even during deferred steps."""

        config = dc.replace(self.config, max_expansion_ratio=2)
        handler = IoPipelineHttpResponseDecompressor(config=config)

        # 10 bytes compressed -> 1000 bytes uncompressed (ratio 100)
        compressor = zlib.compressobj(wbits=16 + zlib.MAX_WBITS)
        bomb_data = compressor.compress(b'A' * 1000) + compressor.flush()

        channel = IoPipeline.new(
            [
                handler,
                ibq := InboundQueueIoPipelineHandler(),  # noqa
            ],
        )
        channel.feed_in(self.head)

        # Feeding this should eventually raise ValueError due to expansion ratio
        channel.feed_in(IoPipelineHttpResponseBodyData(bomb_data))
        count = 0
        while (out := channel.output.poll()) is not None:
            count += 1
            if count > 100:
                self.fail('Infinite defer loop')
            dfl = check.isinstance(out, IoPipelineMessages.Defer)
            channel.run_deferred(dfl)

        [out_head, *out_data, out_err] = ibq.drain()
        self.assertIs(self.head, out_head)
        err = check.isinstance(out_err, IoPipelineMessages.Error)
        self.assertIsInstance(err.exc, ValueError)
        self.assertIn('expansion ratio exceeds limit', repr(err.exc))

    # def test_manual_read_backpressure_with_defer(self):
    #     """Test that manual read (auto_read=False) correctly stalls the defer loop."""
    #
    #     self.ctx.services[IoPipelineFlow] = StubIoPipelineFlow(auto_read=False)
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
    #     self.handler.outbound(self.ctx, IoPipelineFlowMessages.ReadyForInput())
    #
    #     # Now one chunk should be present
    #     self.assertGreater(len(self.ctx.inbound_results), 0)
