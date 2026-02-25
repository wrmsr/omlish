# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import unittest

from omlish.http.headers import HttpHeaders
from omlish.http.versions import HttpVersion

from ....core import PipelineChannel
from ....handlers.feedback import FeedbackInboundChannelPipelineHandler
from ...requests import FullPipelineHttpRequest
from ...requests import PipelineHttpRequestContentChunkData
from ...requests import PipelineHttpRequestEnd
from ...requests import PipelineHttpRequestHead
from ..requests import PipelineHttpRequestEncoder


class TestPipelineHttpRequestEncoder(unittest.TestCase):
    def test_basic_get_request(self) -> None:
        """Test basic GET request encoding."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        request = FullPipelineHttpRequest(
            head=PipelineHttpRequestHead(
                method='GET',
                target='/index.html',
                version=HttpVersion(1, 1),
                headers=HttpHeaders([
                    ('Host', 'example.com'),
                    ('User-Agent', 'TestClient/1.0'),
                ]),
            ),
            body=b'',
        )

        channel.feed_in(fbi.wrap(request))
        out = channel.output.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'GET /index.html HTTP/1.1\r\n'
            b'Host: example.com\r\n'
            b'User-Agent: TestClient/1.0\r\n'
            b'\r\n'
        )

        self.assertEqual(encoded, expected)

    def test_post_request_with_body(self) -> None:
        """Test POST request with body."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        body = b'name=value&foo=bar'

        request = FullPipelineHttpRequest(
            head=PipelineHttpRequestHead(
                method='POST',
                target='/submit',
                version=HttpVersion(1, 1),
                headers=HttpHeaders([
                    ('Host', 'example.com'),
                    ('Content-Type', 'application/x-www-form-urlencoded'),
                    ('Content-Length', str(len(body))),
                ]),
            ),
            body=body,
        )

        channel.feed_in(fbi.wrap(request))
        out = channel.output.drain()

        self.assertEqual(out, [
            b'POST /submit HTTP/1.1\r\n'
            b'Host: example.com\r\n'
            b'Content-Type: application/x-www-form-urlencoded\r\n'
            b'Content-Length: 18\r\n'
            b'\r\n',
            b'name=value&foo=bar',
        ])

    def test_put_request(self) -> None:
        """Test PUT request encoding."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        body = b'{"key": "value"}'

        request = FullPipelineHttpRequest(
            head=PipelineHttpRequestHead(
                method='PUT',
                target='/api/resource/123',
                version=HttpVersion(1, 1),
                headers=HttpHeaders([
                    ('Host', 'api.example.com'),
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(body))),
                ]),
            ),
            body=body,
        )

        channel.feed_in(fbi.wrap(request))
        out = channel.output.drain()

        self.assertEqual(out, [
            b'PUT /api/resource/123 HTTP/1.1\r\n'
            b'Host: api.example.com\r\n'
            b'Content-Type: application/json\r\n'
            b'Content-Length: 16\r\n'
            b'\r\n',
            b'{"key": "value"}',
        ])

    def test_delete_request(self) -> None:
        """Test DELETE request encoding."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        request = FullPipelineHttpRequest(
            head=PipelineHttpRequestHead(
                method='DELETE',
                target='/api/resource/456',
                version=HttpVersion(1, 1),
                headers=HttpHeaders([
                    ('Host', 'api.example.com'),
                ]),
            ),
            body=b'',
        )

        channel.feed_in(fbi.wrap(request))
        out = channel.output.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'DELETE /api/resource/456 HTTP/1.1\r\n'
            b'Host: api.example.com\r\n'
            b'\r\n'
        )

        self.assertEqual(encoded, expected)

    def test_http_1_0_request(self) -> None:
        """Test HTTP/1.0 request."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        request = FullPipelineHttpRequest(
            head=PipelineHttpRequestHead(
                method='GET',
                target='/page.html',
                version=HttpVersion(1, 0),
                headers=HttpHeaders([
                    ('Host', 'example.com'),
                ]),
            ),
            body=b'',
        )

        channel.feed_in(fbi.wrap(request))
        out = channel.output.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'GET /page.html HTTP/1.0\r\n'
            b'Host: example.com\r\n'
            b'\r\n'
        )

        self.assertEqual(encoded, expected)

    def test_multiple_headers(self) -> None:
        """Test request with multiple headers."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        request = FullPipelineHttpRequest(
            head=PipelineHttpRequestHead(
                method='GET',
                target='/',
                version=HttpVersion(1, 1),
                headers=HttpHeaders([
                    ('Host', 'example.com'),
                    ('User-Agent', 'TestClient/1.0'),
                    ('Accept', 'text/html'),
                    ('Accept-Encoding', 'gzip, deflate'),
                    ('Connection', 'keep-alive'),
                ]),
            ),
            body=b'',
        )

        channel.feed_in(fbi.wrap(request))
        out = channel.output.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'GET / HTTP/1.1\r\n'
            b'Host: example.com\r\n'
            b'User-Agent: TestClient/1.0\r\n'
            b'Accept: text/html\r\n'
            b'Accept-Encoding: gzip, deflate\r\n'
            b'Connection: keep-alive\r\n'
            b'\r\n'
        )

        self.assertEqual(encoded, expected)

    def test_absolute_uri_target(self) -> None:
        """Test request with absolute URI as target."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        request = FullPipelineHttpRequest(
            head=PipelineHttpRequestHead(
                method='GET',
                target='http://example.com:8080/path?query=value',
                version=HttpVersion(1, 1),
                headers=HttpHeaders([
                    ('Host', 'example.com:8080'),
                ]),
            ),
            body=b'',
        )

        channel.feed_in(fbi.wrap(request))
        out = channel.output.drain()

        self.assertEqual(len(out), 1)
        encoded = out[0]

        expected = (
            b'GET http://example.com:8080/path?query=value HTTP/1.1\r\n'
            b'Host: example.com:8080\r\n'
            b'\r\n'
        )

        self.assertEqual(encoded, expected)

    def test_streaming_request_no_chunked(self) -> None:
        """Test streaming request without chunked encoding."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        # Send head
        head = PipelineHttpRequestHead(
            method='POST',
            target='/upload',
            version=HttpVersion(1, 1),
            headers=HttpHeaders([
                ('Host', 'example.com'),
                ('Content-Length', '11'),
            ]),
        )
        channel.feed_in(fbi.wrap(head))

        # Send chunks
        channel.feed_in(fbi.wrap(PipelineHttpRequestContentChunkData(b'hello')))
        channel.feed_in(fbi.wrap(PipelineHttpRequestContentChunkData(b' ')))
        channel.feed_in(fbi.wrap(PipelineHttpRequestContentChunkData(b'world')))

        # Send end
        channel.feed_in(fbi.wrap(PipelineHttpRequestEnd()))

        out = channel.output.drain()

        # Should get: head, then 3 data chunks, then nothing (end consumed)
        self.assertEqual(len(out), 4)

        # Head
        self.assertEqual(
            out[0],
            b'POST /upload HTTP/1.1\r\n'
            b'Host: example.com\r\n'
            b'Content-Length: 11\r\n'
            b'\r\n',
        )

        # Chunks (raw, no chunked encoding)
        self.assertEqual(out[1], b'hello')
        self.assertEqual(out[2], b' ')
        self.assertEqual(out[3], b'world')

    def test_streaming_request_with_chunked_encoding(self) -> None:
        """Test streaming request with chunked encoding."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        # Send head with Transfer-Encoding: chunked
        head = PipelineHttpRequestHead(
            method='POST',
            target='/upload',
            version=HttpVersion(1, 1),
            headers=HttpHeaders([
                ('Host', 'example.com'),
                ('Transfer-Encoding', 'chunked'),
            ]),
        )
        channel.feed_in(fbi.wrap(head))

        # Send chunks
        channel.feed_in(fbi.wrap(PipelineHttpRequestContentChunkData(b'hello')))
        channel.feed_in(fbi.wrap(PipelineHttpRequestContentChunkData(b'world')))

        # Send end
        channel.feed_in(fbi.wrap(PipelineHttpRequestEnd()))

        out = channel.output.drain()

        # Should get: head, chunked data, terminator
        self.assertEqual(len(out), 8)

        # Head
        self.assertEqual(
            out[0],
            b'POST /upload HTTP/1.1\r\n'
            b'Host: example.com\r\n'
            b'Transfer-Encoding: chunked\r\n'
            b'\r\n',
        )

        # First chunk: 5\r\nhello\r\n
        self.assertEqual(out[1], b'5\r\n')
        self.assertEqual(out[2], b'hello')
        self.assertEqual(out[3], b'\r\n')

        # Second chunk: 5\r\nworld\r\n
        self.assertEqual(out[4], b'5\r\n')
        self.assertEqual(out[5], b'world')
        self.assertEqual(out[6], b'\r\n')

        # Terminator: 0\r\n\r\n
        self.assertEqual(out[7], b'0\r\n\r\n')

    def test_streaming_empty_chunk_not_emitted(self) -> None:
        """Test that empty chunks don't emit data."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        head = PipelineHttpRequestHead(
            method='POST',
            target='/data',
            version=HttpVersion(1, 1),
            headers=HttpHeaders([
                ('Host', 'example.com'),
                ('Content-Length', '5'),
            ]),
        )
        channel.feed_in(fbi.wrap(head))

        # Empty chunks should not emit
        channel.feed_in(fbi.wrap(PipelineHttpRequestContentChunkData(b'')))
        channel.feed_in(fbi.wrap(PipelineHttpRequestContentChunkData(b'hello')))
        channel.feed_in(fbi.wrap(PipelineHttpRequestContentChunkData(b'')))

        channel.feed_in(fbi.wrap(PipelineHttpRequestEnd()))

        out = channel.output.drain()

        # Head + single data chunk
        self.assertEqual(len(out), 2)
        self.assertEqual(out[1], b'hello')

    def test_multiple_requests(self) -> None:
        """Test encoding multiple sequential requests."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        # First request
        req1 = FullPipelineHttpRequest(
            head=PipelineHttpRequestHead(
                method='GET',
                target='/first',
                version=HttpVersion(1, 1),
                headers=HttpHeaders([('Host', 'example.com')]),
            ),
            body=b'',
        )
        channel.feed_in(fbi.wrap(req1))

        # Second request
        req2 = FullPipelineHttpRequest(
            head=PipelineHttpRequestHead(
                method='POST',
                target='/second',
                version=HttpVersion(1, 1),
                headers=HttpHeaders([
                    ('Host', 'example.com'),
                    ('Content-Length', '4'),
                ]),
            ),
            body=b'data',
        )
        channel.feed_in(fbi.wrap(req2))

        out = channel.output.drain()

        self.assertEqual(out, [
            b'GET /first HTTP/1.1\r\n'
            b'Host: example.com\r\n'
            b'\r\n',

            b'POST /second HTTP/1.1\r\n'
            b'Host: example.com\r\n'
            b'Content-Length: 4\r\n'
            b'\r\n',

            b'data',
        ])

    def test_passthrough_unknown_message(self) -> None:
        """Test that unknown messages pass through unchanged."""

        encoder = PipelineHttpRequestEncoder()
        channel = PipelineChannel.new([
            encoder,
            fbi := FeedbackInboundChannelPipelineHandler(),
        ])

        class UnknownMessage:
            pass

        msg = UnknownMessage()
        channel.feed_in(fbi.wrap(msg))

        out = channel.output.drain()
        self.assertEqual(len(out), 1)
        self.assertIs(out[0], msg)
