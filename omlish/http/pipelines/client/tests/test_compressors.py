# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import unittest
import zlib

from .....io.pipelines.core import IoPipeline
from .....io.pipelines.handlers.feedback import FeedbackInboundIoPipelineHandler
from .....lite.check import check
from ....headers import HttpHeaders
from ...requests import IoPipelineHttpRequestBodyData
from ...requests import IoPipelineHttpRequestEnd
from ...requests import IoPipelineHttpRequestHead
from ..requests import IoPipelineHttpRequestCompressor


class TestGzipCompressorSimple(unittest.TestCase):
    """Simple compression tests without flow control complexity."""

    def test_passthrough_no_encoding(self):
        """Test that data passes through unchanged when no content-encoding is present."""

        handler = IoPipelineHttpRequestCompressor()

        channel = IoPipeline.new([
            handler,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        # Head without content-encoding
        head = IoPipelineHttpRequestHead(
            method='POST',
            target='/api/data',
            headers=HttpHeaders({}),
        )

        # Feed messages
        channel.feed_in(fbi.wrap(head))
        channel.feed_in(fbi.wrap(IoPipelineHttpRequestBodyData(b'Hello, World!')))
        channel.feed_in(fbi.wrap(IoPipelineHttpRequestEnd()))

        # Verify passthrough
        results = channel.output.drain()
        self.assertEqual(len(results), 3)
        self.assertIs(results[0], head)
        self.assertEqual(check.isinstance(results[1], IoPipelineHttpRequestBodyData).data, b'Hello, World!')
        self.assertIsInstance(results[2], IoPipelineHttpRequestEnd)

    def test_simple_gzip_compression(self):
        """Test basic gzip compression with default config."""

        handler = IoPipelineHttpRequestCompressor()

        channel = IoPipeline.new([
            handler,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        # Create raw data
        raw_data = b'Hello, World!'

        # Head with gzip encoding
        head = IoPipelineHttpRequestHead(
            method='POST',
            target='/api/data',
            headers=HttpHeaders({'content-encoding': 'gzip'}),
        )

        # Feed messages
        channel.feed_in(fbi.wrap(head))
        channel.feed_in(fbi.wrap(IoPipelineHttpRequestBodyData(raw_data)))
        channel.feed_in(fbi.wrap(end := IoPipelineHttpRequestEnd()))

        # Verify compression
        results = channel.output.drain()
        self.assertTrue(len(results) < 5)  # Should only be 1-2 data chunks
        self.assertIs(results[0], head)
        self.assertIs(results[-1], end)

        compressed_data = b''.join([
            check.isinstance(r, IoPipelineHttpRequestBodyData).data
            for r in results[1:-1]
        ])

        # Verify by decompressing
        decompressor = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
        decompressed = decompressor.decompress(compressed_data) + decompressor.flush()
        self.assertEqual(decompressed, raw_data)

    def test_gzip_multiple_chunks(self):
        """Test gzip compression with multiple body data chunks."""

        handler = IoPipelineHttpRequestCompressor()

        channel = IoPipeline.new([
            handler,
            fbi := FeedbackInboundIoPipelineHandler(),
        ])

        # Create raw data chunks
        chunk1 = b'This is the first chunk. '
        chunk2 = b'This is the second chunk. '
        chunk3 = b'This is the third chunk.'
        raw_data = chunk1 + chunk2 + chunk3

        # Head with gzip encoding
        head = IoPipelineHttpRequestHead(
            method='POST',
            target='/api/data',
            headers=HttpHeaders({'content-encoding': 'gzip'}),
        )

        # Feed messages
        channel.feed_in(fbi.wrap(head))
        channel.feed_in(fbi.wrap(IoPipelineHttpRequestBodyData(chunk1)))
        channel.feed_in(fbi.wrap(IoPipelineHttpRequestBodyData(chunk2)))
        channel.feed_in(fbi.wrap(IoPipelineHttpRequestBodyData(chunk3)))
        channel.feed_in(fbi.wrap(IoPipelineHttpRequestEnd()))

        # Verify compression - collect all body data
        results = channel.output.drain()
        self.assertIs(results[0], head)

        body_data_msgs = [m for m in results[1:-1] if isinstance(m, IoPipelineHttpRequestBodyData)]
        compressed = b''.join(m.data for m in body_data_msgs)

        # Verify by decompressing
        decompressor = zlib.decompressobj(wbits=16 + zlib.MAX_WBITS)
        decompressed = decompressor.decompress(compressed) + decompressor.flush()
        self.assertEqual(decompressed, raw_data)

        self.assertIsInstance(results[-1], IoPipelineHttpRequestEnd)
