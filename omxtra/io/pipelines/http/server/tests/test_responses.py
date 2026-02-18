# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import unittest

from omlish.http.headers import HttpHeaders
from omlish.http.versions import HttpVersion

from ....core import PipelineChannel
from ...responses import FullPipelineHttpResponse
from ...responses import PipelineHttpResponseContentChunk
from ...responses import PipelineHttpResponseEnd
from ...responses import PipelineHttpResponseHead
from ..responses import PipelineHttpResponseEncoder


TERMINAL_EMIT_CHANNEL_CONFIG = PipelineChannel.Config(
    pipeline=PipelineChannel.PipelineConfig(
        terminal_mode='emit',
    ),
)


class TestPipelineHttpResponseEncoder(unittest.TestCase):
    def test_basic_response(self) -> None:
        """Test basic HTTP response encoding."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 1),
                status=200,
                reason='OK',
                headers=HttpHeaders([
                    ('Content-Type', 'text/plain'),
                    ('Content-Length', '5'),
                ]),
            ),
            body=b'hello',
        )

        channel.feed_out(response)
        out = channel.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: text/plain\r\n'
            b'Content-Length: 5\r\n'
            b'\r\n'
            b'hello'
        )

        self.assertEqual(encoded, expected)

    def test_404_response(self) -> None:
        """Test 404 response encoding."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 1),
                status=404,
                reason='Not Found',
                headers=HttpHeaders([
                    ('Content-Type', 'text/plain'),
                    ('Content-Length', '9'),
                ]),
            ),
            body=b'not found',
        )

        channel.feed_out(response)
        out = channel.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'HTTP/1.1 404 Not Found\r\n'
            b'Content-Type: text/plain\r\n'
            b'Content-Length: 9\r\n'
            b'\r\n'
            b'not found'
        )

        self.assertEqual(encoded, expected)

    def test_empty_body(self) -> None:
        """Test response with empty body."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 1),
                status=204,
                reason='No Content',
                headers=HttpHeaders([
                    ('Content-Length', '0'),
                ]),
            ),
            body=b'',
        )

        channel.feed_out(response)
        out = channel.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'HTTP/1.1 204 No Content\r\n'
            b'Content-Length: 0\r\n'
            b'\r\n'
        )

        self.assertEqual(encoded, expected)

    def test_multiple_headers(self) -> None:
        """Test response with multiple headers."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 1),
                status=200,
                reason='OK',
                headers=HttpHeaders([
                    ('Content-Type', 'text/html; charset=utf-8'),
                    ('Content-Length', '4'),
                    ('Connection', 'close'),
                    ('Cache-Control', 'no-cache'),
                    ('X-Custom-Header', 'custom-value'),
                ]),
            ),
            body=b'test',
        )

        channel.feed_out(response)
        out = channel.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        # Verify status line
        self.assertTrue(encoded.startswith(b'HTTP/1.1 200 OK\r\n'))

        # Verify all headers present
        self.assertIn(b'Content-Type: text/html; charset=utf-8\r\n', encoded)
        self.assertIn(b'Content-Length: 4\r\n', encoded)
        self.assertIn(b'Connection: close\r\n', encoded)
        self.assertIn(b'Cache-Control: no-cache\r\n', encoded)
        self.assertIn(b'X-Custom-Header: custom-value\r\n', encoded)

        # Verify body
        self.assertTrue(encoded.endswith(b'\r\n\r\ntest'))

    def test_http_10_version(self) -> None:
        """Test HTTP/1.0 version encoding."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 0),
                status=200,
                reason='OK',
                headers=HttpHeaders([
                    ('Content-Length', '2'),
                ]),
            ),
            body=b'ok',
        )

        channel.feed_out(response)
        out = channel.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        self.assertTrue(encoded.startswith(b'HTTP/1.0 200 OK\r\n'))

    def test_large_body(self) -> None:
        """Test response with large body."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        body = b'x' * 10000

        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 1),
                status=200,
                reason='OK',
                headers=HttpHeaders([
                    ('Content-Type', 'application/octet-stream'),
                    ('Content-Length', str(len(body))),
                ]),
            ),
            body=body,
        )

        channel.feed_out(response)
        out = channel.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        # Verify body is present and correct
        self.assertTrue(encoded.endswith(body))
        self.assertIn(b'Content-Length: 10000\r\n', encoded)

    def test_duplicate_header_names(self) -> None:
        """Test response with duplicate header names (e.g., Set-Cookie)."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 1),
                status=200,
                reason='OK',
                headers=HttpHeaders([
                    ('Set-Cookie', 'session=abc123'),
                    ('Set-Cookie', 'user=john'),
                    ('Content-Length', '0'),
                ]),
            ),
            body=b'',
        )

        channel.feed_out(response)
        out = channel.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        # Both Set-Cookie headers should be present
        lines = encoded.split(b'\r\n')
        set_cookie_lines = [line for line in lines if line.startswith(b'Set-Cookie:')]
        self.assertEqual(len(set_cookie_lines), 2)
        self.assertIn(b'Set-Cookie: session=abc123', set_cookie_lines)
        self.assertIn(b'Set-Cookie: user=john', set_cookie_lines)

    def test_pass_through_non_response_messages(self) -> None:
        """Test that non-response messages pass through unchanged."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        # Send various non-response messages
        channel.feed_out(b'raw bytes')
        channel.feed_out('string message')
        channel.feed_out(42)

        out = channel.drain()

        self.assertEqual(len(out), 3)
        self.assertEqual(out[0], b'raw bytes')
        self.assertEqual(out[1], 'string message')
        self.assertEqual(out[2], 42)

    def test_mixed_messages(self) -> None:
        """Test encoding responses mixed with other messages."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        # Send response
        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 1),
                status=200,
                reason='OK',
                headers=HttpHeaders([
                    ('Content-Length', '2'),
                ]),
            ),
            body=b'ok',
        )
        channel.feed_out(response)

        # Send non-response
        channel.feed_out(b'other data')

        out = channel.drain()

        self.assertEqual(len(out), 2)

        # First should be encoded response
        self.assertIn(b'HTTP/1.1 200 OK\r\n', out[0])

        # Second should be unchanged
        self.assertEqual(out[1], b'other data')

    def test_redirect_response(self) -> None:
        """Test 302 redirect response."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 1),
                status=302,
                reason='Found',
                headers=HttpHeaders([
                    ('Location', 'https://example.com/new-path'),
                    ('Content-Length', '0'),
                ]),
            ),
            body=b'',
        )

        channel.feed_out(response)
        out = channel.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'HTTP/1.1 302 Found\r\n'
            b'Location: https://example.com/new-path\r\n'
            b'Content-Length: 0\r\n'
            b'\r\n'
        )

        self.assertEqual(encoded, expected)

    def test_server_error_response(self) -> None:
        """Test 500 server error response."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        response = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                version=HttpVersion(1, 1),
                status=500,
                reason='Internal Server Error',
                headers=HttpHeaders([
                    ('Content-Type', 'text/plain'),
                    ('Content-Length', '13'),
                ]),
            ),
            body=b'server error!',
        )

        channel.feed_out(response)
        out = channel.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'HTTP/1.1 500 Internal Server Error\r\n'
            b'Content-Type: text/plain\r\n'
            b'Content-Length: 13\r\n'
            b'\r\n'
            b'server error!'
        )

        self.assertEqual(encoded, expected)


class TestPipelineHttpResponseEncoderStreaming(unittest.TestCase):
    def test_streaming_response_with_content_length(self) -> None:
        """Test streaming response with Content-Length (no chunked encoding)."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        # Send head
        channel.feed_out(PipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Content-Type', 'text/plain'),
                ('Content-Length', '10'),
            ]),
        ))

        # Send body chunks
        channel.feed_out(PipelineHttpResponseContentChunk(b'hello'))
        channel.feed_out(PipelineHttpResponseContentChunk(b'world'))

        # Send end
        channel.feed_out(PipelineHttpResponseEnd())

        out = channel.drain()

        # Should get: head bytes, chunk1, chunk2
        self.assertEqual(len(out), 3)

        # Head
        head = out[0]
        self.assertIn(b'HTTP/1.1 200 OK\r\n', head)
        self.assertIn(b'Content-Type: text/plain\r\n', head)
        self.assertIn(b'Content-Length: 10\r\n', head)
        self.assertTrue(head.endswith(b'\r\n'))

        # Chunks (raw bytes, no chunked encoding)
        self.assertEqual(out[1], b'hello')
        self.assertEqual(out[2], b'world')

    def test_streaming_response_with_chunked_encoding(self) -> None:
        """Test streaming response with Transfer-Encoding: chunked."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        # Send head with Transfer-Encoding: chunked
        channel.feed_out(PipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Content-Type', 'text/plain'),
                ('Transfer-Encoding', 'chunked'),
            ]),
        ))

        # Send body chunks
        channel.feed_out(PipelineHttpResponseContentChunk(b'hello'))
        channel.feed_out(PipelineHttpResponseContentChunk(b'world'))

        # Send end
        channel.feed_out(PipelineHttpResponseEnd())

        out = channel.drain()

        # Should get: head, chunk1 (size+data+crlf), chunk2 (size+data+crlf), terminator
        self.assertEqual(len(out), 8)

        # Head
        head = out[0]
        self.assertIn(b'HTTP/1.1 200 OK\r\n', head)
        self.assertIn(b'Transfer-Encoding: chunked\r\n', head)

        # First chunk: 5\r\nhello\r\n
        self.assertEqual(out[1], b'5\r\n')
        self.assertEqual(out[2], b'hello')
        self.assertEqual(out[3], b'\r\n')

        # Second chunk: 5\r\nworld\r\n
        self.assertEqual(out[4], b'5\r\n')
        self.assertEqual(out[5], b'world')
        self.assertEqual(out[6], b'\r\n')

        # Terminator
        self.assertEqual(out[7], b'0\r\n\r\n')

    def test_streaming_response_chunked_terminator(self) -> None:
        """Test that chunked encoding emits final terminator."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        channel.feed_out(PipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Transfer-Encoding', 'chunked'),
            ]),
        ))

        channel.feed_out(PipelineHttpResponseContentChunk(b'data'))
        channel.feed_out(PipelineHttpResponseEnd())

        out = channel.drain()

        # Last message should be the terminator
        self.assertEqual(out[-1], b'0\r\n\r\n')

    def test_streaming_empty_chunks_ignored(self) -> None:
        """Test that empty chunks don't emit bytes."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        channel.feed_out(PipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Content-Length', '5'),
            ]),
        ))

        channel.feed_out(PipelineHttpResponseContentChunk(b''))  # Empty - should be ignored
        channel.feed_out(PipelineHttpResponseContentChunk(b'hello'))
        channel.feed_out(PipelineHttpResponseContentChunk(b''))  # Empty - should be ignored
        channel.feed_out(PipelineHttpResponseEnd())

        out = channel.drain()

        # Should only get head + 1 chunk
        self.assertEqual(len(out), 2)
        self.assertIn(b'HTTP/1.1 200 OK\r\n', out[0])
        self.assertEqual(out[1], b'hello')

    def test_streaming_multiple_responses(self) -> None:
        """Test that encoder resets state between responses."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        # First response (chunked)
        channel.feed_out(PipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Transfer-Encoding', 'chunked'),
            ]),
        ))
        channel.feed_out(PipelineHttpResponseContentChunk(b'first'))
        channel.feed_out(PipelineHttpResponseEnd())

        # Second response (Content-Length)
        channel.feed_out(PipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Content-Length', '6'),
            ]),
        ))
        channel.feed_out(PipelineHttpResponseContentChunk(b'second'))
        channel.feed_out(PipelineHttpResponseEnd())

        out = channel.drain()

        # Verify first response was chunked
        self.assertIn(b'5\r\n', out)
        self.assertIn(b'first', out)
        self.assertIn(b'0\r\n\r\n', out)

        # Verify second response was NOT chunked (raw bytes)
        self.assertIn(b'second', out)

    def test_streaming_large_chunk_hex_encoding(self) -> None:
        """Test chunked encoding with larger chunk sizes."""

        encoder = PipelineHttpResponseEncoder()
        channel = PipelineChannel([encoder], TERMINAL_EMIT_CHANNEL_CONFIG)

        channel.feed_out(PipelineHttpResponseHead(
            version=HttpVersion(1, 1),
            status=200,
            reason='OK',
            headers=HttpHeaders([
                ('Transfer-Encoding', 'chunked'),
            ]),
        ))

        # 256 byte chunk -> 100 in hex
        data = b'x' * 256
        channel.feed_out(PipelineHttpResponseContentChunk(data))
        channel.feed_out(PipelineHttpResponseEnd())

        out = channel.drain()

        # Check hex size is correct
        self.assertIn(b'100\r\n', out)  # 256 = 0x100
        self.assertIn(data, out)
