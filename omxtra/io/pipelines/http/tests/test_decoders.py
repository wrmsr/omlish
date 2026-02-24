# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta
import unittest

from omlish.http.parsing import HttpParser
from omlish.http.parsing import ParsedHttpMessage

from ...core import ChannelPipelineMessages
from ..decoders import PipelineHttpDecodingConfig
from ..decoders import PipelineHttpHeadDecoder


class TestPipelineHttpHeadDecoder(unittest.TestCase):
    """
    Unit tests for PipelineHttpHeadDecoder.

    Focuses on boundary handling: feeding data in chunks split at various positions to ensure correct buffering and
    parsing regardless of how the bytes arrive.
    """

    def _make_head(self, parsed: ParsedHttpMessage) -> str:
        """Test callback that returns a simple marker."""

        return f'HEAD:{parsed.kind.value}'

    def _make_aborted(self, reason: str) -> str:
        """Test callback that returns an abort marker."""

        return f'ABORTED:{reason}'

    def test_complete_request_single_chunk(self) -> None:
        """Test parsing a complete HTTP request head in a single chunk."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        raw = b'GET /path HTTP/1.1\r\nHost: example.com\r\nContent-Length: 5\r\n\r\n'
        out = decoder.inbound(raw)

        self.assertEqual(len(out), 1)
        self.assertEqual(out[0], 'HEAD:request')
        self.assertTrue(decoder.done)

    def test_complete_response_single_chunk(self) -> None:
        """Test parsing a complete HTTP response head in a single chunk."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.RESPONSE,
            self._make_head,
            self._make_aborted,
        )

        raw = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 12\r\n\r\n'
        out = decoder.inbound(raw)

        self.assertEqual(len(out), 1)
        self.assertEqual(out[0], 'HEAD:response')
        self.assertTrue(decoder.done)

    def test_head_with_body_remainder(self) -> None:
        """Test that remainder bytes after head are forwarded."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        raw = b'GET / HTTP/1.1\r\nHost: test\r\n\r\nBODYDATA'
        out = decoder.inbound(raw)

        self.assertEqual(len(out), 2)
        self.assertEqual(out[0], 'HEAD:request')
        # Second output should be the remainder bytes
        self.assertEqual(out[1].tobytes(), b'BODYDATA')
        self.assertTrue(decoder.done)

    def test_split_in_request_line(self) -> None:
        """Test head split in the middle of the request line."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        chunk1 = b'GET /pa'
        chunk2 = b'th HTTP/1.1\r\nHost: example.com\r\n\r\n'

        out1 = decoder.inbound(chunk1)
        self.assertEqual(len(out1), 0)
        self.assertFalse(decoder.done)

        out2 = decoder.inbound(chunk2)
        self.assertEqual(len(out2), 1)
        self.assertEqual(out2[0], 'HEAD:request')
        self.assertTrue(decoder.done)

    def test_split_after_request_line(self) -> None:
        """Test head split right after the request line."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        chunk1 = b'GET /path HTTP/1.1\r\n'
        chunk2 = b'Host: example.com\r\n\r\n'

        out1 = decoder.inbound(chunk1)
        self.assertEqual(len(out1), 0)

        out2 = decoder.inbound(chunk2)
        self.assertEqual(len(out2), 1)
        self.assertEqual(out2[0], 'HEAD:request')

    def test_split_in_header_line(self) -> None:
        """Test head split in the middle of a header line."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        chunk1 = b'GET / HTTP/1.1\r\nHost: exa'
        chunk2 = b'mple.com\r\n\r\n'

        out1 = decoder.inbound(chunk1)
        self.assertEqual(len(out1), 0)

        out2 = decoder.inbound(chunk2)
        self.assertEqual(len(out2), 1)
        self.assertEqual(out2[0], 'HEAD:request')

    def test_split_in_final_crlf(self) -> None:
        """Test head split in the middle of the final \\r\\n\\r\\n delimiter."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        chunk1 = b'GET / HTTP/1.1\r\nHost: test\r\n\r'
        chunk2 = b'\n'

        out1 = decoder.inbound(chunk1)
        self.assertEqual(len(out1), 0)

        out2 = decoder.inbound(chunk2)
        self.assertEqual(len(out2), 1)
        self.assertEqual(out2[0], 'HEAD:request')

    def test_split_before_final_crlf(self) -> None:
        """Test head split just before the final \\r\\n\\r\\n."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        chunk1 = b'GET / HTTP/1.1\r\nHost: test\r\n'
        chunk2 = b'\r\n'

        out1 = decoder.inbound(chunk1)
        self.assertEqual(len(out1), 0)

        out2 = decoder.inbound(chunk2)
        self.assertEqual(len(out2), 1)
        self.assertEqual(out2[0], 'HEAD:request')

    def test_many_small_chunks(self) -> None:
        """Test head fed in many tiny chunks."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        raw = b'GET / HTTP/1.1\r\nHost: test\r\nContent-Length: 10\r\n\r\n'

        # Feed 3 bytes at a time
        for i in range(0, len(raw) - 3, 3):
            chunk = raw[i:i + 3]
            out = decoder.inbound(chunk)
            if not decoder.done:
                self.assertEqual(len(out), 0)

        # Feed remaining bytes
        if not decoder.done:
            out = decoder.inbound(raw[i + 3:])
            self.assertEqual(len(out), 1)
            self.assertEqual(out[0], 'HEAD:request')

        self.assertTrue(decoder.done)

    def test_byte_by_byte(self) -> None:
        """Test head fed byte by byte."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        raw = b'GET / HTTP/1.1\r\nHost: test\r\n\r\n'

        for i, byte in enumerate(raw):
            chunk = bytes([byte])
            out = decoder.inbound(chunk)

            if i < len(raw) - 1:
                self.assertEqual(len(out), 0)
                self.assertFalse(decoder.done)
            else:
                self.assertEqual(len(out), 1)
                self.assertEqual(out[0], 'HEAD:request')
                self.assertTrue(decoder.done)

    def test_split_with_body_remainder(self) -> None:
        """Test head split across chunks with body remainder."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        chunk1 = b'GET / HTTP/1.1\r\nHost: test\r\n'
        chunk2 = b'\r\nBODYDATA'

        out1 = decoder.inbound(chunk1)
        self.assertEqual(len(out1), 0)

        out2 = decoder.inbound(chunk2)
        self.assertEqual(len(out2), 2)
        self.assertEqual(out2[0], 'HEAD:request')
        self.assertEqual(out2[1].tobytes(), b'BODYDATA')
        self.assertTrue(decoder.done)

    def test_eof_before_complete(self) -> None:
        """Test EOF received before head is complete."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        # Feed partial head
        chunk = b'GET / HTTP/1.1\r\nHost: test\r\n'
        out1 = decoder.inbound(chunk)
        self.assertEqual(len(out1), 0)

        # Send FinalInput
        final_input = ChannelPipelineMessages.FinalInput()
        out2 = decoder.inbound(final_input)

        self.assertEqual(len(out2), 2)
        self.assertEqual(out2[0], 'ABORTED:EOF before HTTP head complete')
        self.assertIs(out2[1], final_input)
        self.assertTrue(decoder.done)

    def test_eof_on_empty_buffer(self) -> None:
        """Test EOF received on empty buffer."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        final_input = ChannelPipelineMessages.FinalInput()
        out = decoder.inbound(final_input)

        self.assertEqual(len(out), 2)
        self.assertEqual(out[0], 'ABORTED:EOF before HTTP head complete')
        self.assertIs(out[1], final_input)
        self.assertTrue(decoder.done)

    def test_non_bytes_message_passthrough(self) -> None:
        """Test that non-bytes messages are passed through."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        msg = {'type': 'control'}
        out = decoder.inbound(msg)

        self.assertEqual(len(out), 1)
        self.assertIs(out[0], msg)
        self.assertFalse(decoder.done)

    def test_buffered_bytes_count(self) -> None:
        """Test inbound_buffered_bytes returns correct count."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        chunk1 = b'GET / HTTP/1.1\r\n'
        decoder.inbound(chunk1)
        self.assertEqual(decoder.inbound_buffered_bytes(), len(chunk1))

        chunk2 = b'Host: test\r\n\r\n'
        decoder.inbound(chunk2)
        self.assertEqual(decoder.inbound_buffered_bytes(), 0)
        self.assertTrue(decoder.done)

    def test_multiple_headers(self) -> None:
        """Test head with multiple headers split across chunks."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        chunk1 = b'GET /api/users HTTP/1.1\r\n'
        chunk2 = b'Host: api.example.com\r\n'
        chunk3 = b'Content-Type: application/json\r\n'
        chunk4 = b'Content-Length: 100\r\n'
        chunk5 = b'Authorization: Bearer token123\r\n\r\n'

        self.assertEqual(len(decoder.inbound(chunk1)), 0)
        self.assertEqual(len(decoder.inbound(chunk2)), 0)
        self.assertEqual(len(decoder.inbound(chunk3)), 0)
        self.assertEqual(len(decoder.inbound(chunk4)), 0)

        out = decoder.inbound(chunk5)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0], 'HEAD:request')
        self.assertTrue(decoder.done)

    def test_response_with_split_status_line(self) -> None:
        """Test response head split in status line."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.RESPONSE,
            self._make_head,
            self._make_aborted,
        )

        chunk1 = b'HTTP/1.1 200'
        chunk2 = b' OK\r\nContent-Length: 0\r\n\r\n'

        out1 = decoder.inbound(chunk1)
        self.assertEqual(len(out1), 0)

        out2 = decoder.inbound(chunk2)
        self.assertEqual(len(out2), 1)
        self.assertEqual(out2[0], 'HEAD:response')

    def test_custom_config(self) -> None:
        """Test decoder with custom configuration."""

        config = PipelineHttpDecodingConfig(
            head_buffer=PipelineHttpDecodingConfig.BufferConfig(
                max_size=2048,
                chunk_size=512,
            ),
        )

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
            config=config,
        )

        raw = b'GET / HTTP/1.1\r\nHost: test\r\n\r\n'
        out = decoder.inbound(raw)

        self.assertEqual(len(out), 1)
        self.assertEqual(out[0], 'HEAD:request')

    def test_empty_bytes_handling(self) -> None:
        """Test that empty bytes are handled gracefully."""

        decoder = PipelineHttpHeadDecoder(
            HttpParser.Mode.REQUEST,
            self._make_head,
            self._make_aborted,
        )

        out1 = decoder.inbound(b'')
        self.assertEqual(len(out1), 0)

        out2 = decoder.inbound(b'GET / HTTP/1.1\r\n')
        self.assertEqual(len(out2), 0)

        out3 = decoder.inbound(b'')
        self.assertEqual(len(out3), 0)

        out4 = decoder.inbound(b'Host: test\r\n\r\n')
        self.assertEqual(len(out4), 1)
        self.assertEqual(out4[0], 'HEAD:request')

    def test_split_across_all_delimiters(self) -> None:
        """Test splitting right at each \\r\\n boundary."""

        raw = b'GET / HTTP/1.1\r\nHost: test\r\nContent-Type: text/plain\r\n\r\n'

        # Find all \r\n positions
        delim_positions: ta.List[int] = []
        i = 0
        while i < len(raw) - 1:
            if raw[i:i + 2] == b'\r\n':
                delim_positions.append(i + 2)  # Position after \r\n
            i += 1

        # For each delimiter position, try splitting there
        for split_pos in delim_positions:
            decoder = PipelineHttpHeadDecoder(
                HttpParser.Mode.REQUEST,
                self._make_head,
                self._make_aborted,
            )

            chunk1 = raw[:split_pos]
            chunk2 = raw[split_pos:]

            out1 = decoder.inbound(chunk1)
            if b'\r\n\r\n' in chunk1:
                self.assertEqual(len(out1), 1)
            else:
                self.assertEqual(len(out1), 0)

            if not decoder.done:
                out2 = decoder.inbound(chunk2)
                self.assertEqual(len(out2), 1)
                self.assertEqual(out2[0], 'HEAD:request')

            self.assertTrue(decoder.done)
