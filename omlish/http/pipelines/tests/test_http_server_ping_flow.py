# ruff: noqa: S310 UP045
# @omlish-lite
import unittest
import urllib.error
import urllib.request

from .demos.http_server_ping_flow import build_http_ping_channel
from .servers import HttpServerRunner


class TestHttpServerPingFlow(unittest.TestCase):
    """
    Integration tests for the HTTP ping server with flow control.

    Functionality is same as regular ping, but uses BytesFlowControlChannelPipelineHandler.
    """

    def test_ping_endpoint(self) -> None:
        """Test GET /ping returns 200 'pong'."""

        with HttpServerRunner(build_http_ping_channel, 8089, use_flow_control=True) as port:
            resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/ping')
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), b'pong')
            self.assertEqual(resp.headers.get('Content-Type'), 'text/plain; charset=utf-8')

    def test_not_found_endpoint(self) -> None:
        """Test unknown path returns 404 'not found'."""

        with HttpServerRunner(build_http_ping_channel, 8089, use_flow_control=True) as port:
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/unknown')
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)
                self.assertEqual(e.read(), b'not found')

    def test_multiple_requests(self) -> None:
        """Test multiple sequential requests work."""

        with HttpServerRunner(build_http_ping_channel, 8089, use_flow_control=True) as port:
            # Multiple requests
            for _ in range(5):
                resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/ping')
                self.assertEqual(resp.status, 200)
                self.assertEqual(resp.read(), b'pong')

    def test_connection_closes_after_response(self) -> None:
        """Test that connection closes after response (Connection: close header)."""

        with HttpServerRunner(build_http_ping_channel, 8089, use_flow_control=True) as port:
            resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/ping')
            self.assertEqual(resp.headers.get('Connection'), 'close')
            resp.read()
