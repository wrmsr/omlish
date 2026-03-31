# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import unittest

from ....io.pipelines.core import IoPipeline
from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.handlers.queues import InboundQueueIoPipelineHandler
from ...headers import HttpHeaders
from ...versions import HttpVersions
from ..requests import FullIoPipelineHttpRequest
from ..requests import IoPipelineHttpRequestEnd
from ..requests import IoPipelineHttpRequestHead
from ..responses import FullIoPipelineHttpResponse
from ..responses import IoPipelineHttpResponseHead
from ..servers.keepalive import IoPipelineHttpServerKeepAliveHandler
from ..servers.requests import IoPipelineHttpRequestAggregatorDecoder
from ..servers.requests import IoPipelineHttpRequestDecoder
from ..servers.responses import IoPipelineHttpResponseEncoder


##


class TestKeepAliveDecision(unittest.TestCase):
    def test_http11_default_keep_alive(self) -> None:
        head = IoPipelineHttpRequestHead(
            method='GET',
            target='/test',
            headers=HttpHeaders([('Host', 'test')]),
            version=HttpVersions.HTTP_1_1,
        )
        self.assertTrue(IoPipelineHttpServerKeepAliveHandler.is_request_keep_alive(head))

    def test_http11_connection_close(self) -> None:
        head = IoPipelineHttpRequestHead(
            method='GET',
            target='/test',
            headers=HttpHeaders([('Host', 'test'), ('Connection', 'close')]),
            version=HttpVersions.HTTP_1_1,
        )
        self.assertFalse(IoPipelineHttpServerKeepAliveHandler.is_request_keep_alive(head))

    def test_http10_default_close(self) -> None:
        head = IoPipelineHttpRequestHead(
            method='GET',
            target='/test',
            headers=HttpHeaders([('Host', 'test')]),
            version=HttpVersions.HTTP_1_0,
        )
        self.assertFalse(IoPipelineHttpServerKeepAliveHandler.is_request_keep_alive(head))

    def test_http10_connection_keep_alive(self) -> None:
        head = IoPipelineHttpRequestHead(
            method='GET',
            target='/test',
            headers=HttpHeaders([('Host', 'test'), ('Connection', 'keep-alive')]),
            version=HttpVersions.HTTP_1_0,
        )
        self.assertTrue(IoPipelineHttpServerKeepAliveHandler.is_request_keep_alive(head))

    def test_http11_connection_close_case_insensitive(self) -> None:
        head = IoPipelineHttpRequestHead(
            method='GET',
            target='/test',
            headers=HttpHeaders([('Host', 'test'), ('Connection', 'Close')]),
            version=HttpVersions.HTTP_1_1,
        )
        self.assertFalse(IoPipelineHttpServerKeepAliveHandler.is_request_keep_alive(head))


##


class _SimpleEchoHandler:
    """Test handler that echoes the request target as the response body. Does NOT emit FinalOutput."""

    from ....io.pipelines.core import IoPipelineHandler as _Base

    class Handler(_Base):
        def inbound(self, ctx, msg):
            if isinstance(msg, FullIoPipelineHttpRequest):
                ctx.feed_out(FullIoPipelineHttpResponse(
                    head=IoPipelineHttpResponseHead(
                        status=200,
                        reason='OK',
                        headers=HttpHeaders([
                            ('Content-Length', str(len(msg.head.target))),
                        ]),
                    ),
                    body=msg.head.target.encode(),
                ))
                return

            ctx.feed_in(msg)


def _make_ka_channel():
    ka = IoPipelineHttpServerKeepAliveHandler()
    echo = _SimpleEchoHandler.Handler()
    channel = IoPipeline.new([
        ka,
        echo,
    ], IoPipeline.Config(inbound_terminal='drop'))
    return channel


class TestKeepAliveHandler(unittest.TestCase):
    def test_keep_alive_no_final_output(self) -> None:
        """HTTP/1.1 request without Connection: close should NOT emit FinalOutput."""

        channel = _make_ka_channel()

        channel.feed_in(FullIoPipelineHttpRequest(
            head=IoPipelineHttpRequestHead(
                method='GET',
                target='/ping',
                headers=HttpHeaders([('Host', 'test')]),
                version=HttpVersions.HTTP_1_1,
            ),
            body=b'',
        ))

        out = channel.output.drain()
        self.assertEqual(len(out), 1)
        resp = out[0]
        self.assertIsInstance(resp, FullIoPipelineHttpResponse)
        self.assertEqual(resp.body, b'/ping')

    def test_connection_close_emits_final_output(self) -> None:
        """HTTP/1.1 request with Connection: close should emit FinalOutput after response."""

        channel = _make_ka_channel()

        channel.feed_in(FullIoPipelineHttpRequest(
            head=IoPipelineHttpRequestHead(
                method='GET',
                target='/ping',
                headers=HttpHeaders([('Host', 'test'), ('Connection', 'close')]),
                version=HttpVersions.HTTP_1_1,
            ),
            body=b'',
        ))

        out = channel.output.drain()
        self.assertEqual(len(out), 2)
        self.assertIsInstance(out[0], FullIoPipelineHttpResponse)
        self.assertIsInstance(out[1], IoPipelineMessages.FinalOutput)

    def test_multiple_requests_keep_alive(self) -> None:
        """Multiple HTTP/1.1 requests on same pipeline - no FinalOutput until Connection: close."""

        channel = _make_ka_channel()

        # First request - keep-alive
        channel.feed_in(FullIoPipelineHttpRequest(
            head=IoPipelineHttpRequestHead(
                method='GET',
                target='/a',
                headers=HttpHeaders([('Host', 'test')]),
                version=HttpVersions.HTTP_1_1,
            ),
            body=b'',
        ))

        out1 = channel.output.drain()
        self.assertEqual(len(out1), 1)
        self.assertIsInstance(out1[0], FullIoPipelineHttpResponse)
        self.assertEqual(out1[0].body, b'/a')

        # Second request - keep-alive
        channel.feed_in(FullIoPipelineHttpRequest(
            head=IoPipelineHttpRequestHead(
                method='GET',
                target='/b',
                headers=HttpHeaders([('Host', 'test')]),
                version=HttpVersions.HTTP_1_1,
            ),
            body=b'',
        ))

        out2 = channel.output.drain()
        self.assertEqual(len(out2), 1)
        self.assertIsInstance(out2[0], FullIoPipelineHttpResponse)
        self.assertEqual(out2[0].body, b'/b')

        # Third request - close
        channel.feed_in(FullIoPipelineHttpRequest(
            head=IoPipelineHttpRequestHead(
                method='GET',
                target='/c',
                headers=HttpHeaders([('Host', 'test'), ('Connection', 'close')]),
                version=HttpVersions.HTTP_1_1,
            ),
            body=b'',
        ))

        out3 = channel.output.drain()
        self.assertEqual(len(out3), 2)
        self.assertIsInstance(out3[0], FullIoPipelineHttpResponse)
        self.assertEqual(out3[0].body, b'/c')
        self.assertIsInstance(out3[1], IoPipelineMessages.FinalOutput)

    def test_final_input_while_idle_emits_final_output(self) -> None:
        """FinalInput (client EOF) while idle should emit FinalOutput."""

        channel = _make_ka_channel()

        # First request - keep-alive
        channel.feed_in(FullIoPipelineHttpRequest(
            head=IoPipelineHttpRequestHead(
                method='GET',
                target='/a',
                headers=HttpHeaders([('Host', 'test')]),
                version=HttpVersions.HTTP_1_1,
            ),
            body=b'',
        ))
        channel.output.drain()

        # Client disconnects
        channel.feed_in(IoPipelineMessages.FinalInput())

        out = channel.output.drain()
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], IoPipelineMessages.FinalOutput)

    def test_sets_connection_close_header_on_response(self) -> None:
        """When closing, should set Connection: close on HTTP/1.1 response."""

        channel = _make_ka_channel()

        channel.feed_in(FullIoPipelineHttpRequest(
            head=IoPipelineHttpRequestHead(
                method='GET',
                target='/x',
                headers=HttpHeaders([('Host', 'test'), ('Connection', 'close')]),
                version=HttpVersions.HTTP_1_1,
            ),
            body=b'',
        ))

        out = channel.output.drain()
        resp = out[0]
        self.assertIsInstance(resp, FullIoPipelineHttpResponse)
        self.assertTrue(resp.head.headers.contains_value('connection', 'close', ignore_case=True))

    def test_http10_default_emits_final_output(self) -> None:
        """HTTP/1.0 without Connection: keep-alive should emit FinalOutput."""

        channel = _make_ka_channel()

        channel.feed_in(FullIoPipelineHttpRequest(
            head=IoPipelineHttpRequestHead(
                method='GET',
                target='/x',
                headers=HttpHeaders([('Host', 'test')]),
                version=HttpVersions.HTTP_1_0,
            ),
            body=b'',
        ))

        out = channel.output.drain()
        self.assertEqual(len(out), 2)
        self.assertIsInstance(out[0], FullIoPipelineHttpResponse)
        self.assertIsInstance(out[1], IoPipelineMessages.FinalOutput)


##


class TestDecoderMultiMessage(unittest.TestCase):
    def test_decoder_parses_two_messages(self) -> None:
        """Decoder should parse multiple HTTP messages from a single byte stream."""

        decoder = IoPipelineHttpRequestDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ], IoPipeline.Config(inbound_terminal='drop'))

        wire = (
            b'GET /first HTTP/1.1\r\nHost: test\r\n\r\n'
            b'GET /second HTTP/1.1\r\nHost: test\r\nConnection: close\r\n\r\n'
        )
        channel.feed_in(wire)

        out = ibq.drain()

        heads = [m for m in out if isinstance(m, IoPipelineHttpRequestHead)]
        ends = [m for m in out if isinstance(m, IoPipelineHttpRequestEnd)]
        self.assertEqual(len(heads), 2)
        self.assertEqual(len(ends), 2)
        self.assertEqual(heads[0].target, '/first')
        self.assertEqual(heads[1].target, '/second')

    def test_decoder_parses_two_messages_with_bodies(self) -> None:
        """Decoder should parse multiple HTTP messages with Content-Length bodies."""

        decoder = IoPipelineHttpRequestDecoder()
        channel = IoPipeline.new([
            decoder,
            ibq := InboundQueueIoPipelineHandler(),
        ], IoPipeline.Config(inbound_terminal='drop'))

        wire = (
            b'POST /a HTTP/1.1\r\nHost: test\r\nContent-Length: 5\r\n\r\nhello'
            b'POST /b HTTP/1.1\r\nHost: test\r\nContent-Length: 5\r\n\r\nworld'
        )
        channel.feed_in(wire)

        out = ibq.drain()
        heads = [m for m in out if isinstance(m, IoPipelineHttpRequestHead)]
        self.assertEqual(len(heads), 2)
        self.assertEqual(heads[0].target, '/a')
        self.assertEqual(heads[1].target, '/b')


##


class TestKeepAliveFullPipeline(unittest.TestCase):
    def test_full_pipeline_two_requests(self) -> None:
        """Full pipeline: Decoder -> Aggregator -> KeepAlive -> Echo, two requests on same connection."""

        echo = _SimpleEchoHandler.Handler()
        channel = IoPipeline.new([
            IoPipelineHttpRequestDecoder(),
            IoPipelineHttpRequestAggregatorDecoder(),
            IoPipelineHttpResponseEncoder(),
            IoPipelineHttpServerKeepAliveHandler(),
            echo,
        ], IoPipeline.Config(inbound_terminal='drop'))

        # First request
        channel.feed_in(b'GET /first HTTP/1.1\r\nHost: test\r\n\r\n')

        out1 = channel.output.drain()
        wire1 = b''.join(m for m in out1 if isinstance(m, bytes))
        self.assertIn(b'HTTP/1.1 200 OK\r\n', wire1)
        self.assertIn(b'/first', wire1)
        self.assertFalse(any(isinstance(m, IoPipelineMessages.FinalOutput) for m in out1))

        # Second request with Connection: close
        channel.feed_in(b'GET /second HTTP/1.1\r\nHost: test\r\nConnection: close\r\n\r\n')

        out2 = channel.output.drain()
        self.assertIsInstance(out2[-1], IoPipelineMessages.FinalOutput)
        wire2 = b''.join(m for m in out2 if isinstance(m, bytes))
        self.assertIn(b'/second', wire2)
        self.assertIn(b'Connection: close\r\n', wire2)

    def test_full_pipeline_final_input_closes(self) -> None:
        """Full pipeline: client EOF after keep-alive request should close connection."""

        echo = _SimpleEchoHandler.Handler()
        channel = IoPipeline.new([
            IoPipelineHttpRequestDecoder(),
            IoPipelineHttpRequestAggregatorDecoder(),
            IoPipelineHttpResponseEncoder(),
            IoPipelineHttpServerKeepAliveHandler(),
            echo,
        ], IoPipeline.Config(inbound_terminal='drop'))

        channel.feed_in(b'GET /test HTTP/1.1\r\nHost: test\r\n\r\n')
        channel.output.drain()

        channel.feed_final_input()

        out = channel.output.drain()
        self.assertEqual(len(out), 1)
        self.assertIsInstance(out[0], IoPipelineMessages.FinalOutput)
