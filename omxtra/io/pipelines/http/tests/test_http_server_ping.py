# ruff: noqa: UP045
# @omlish-lite
import unittest
import urllib.error
import urllib.request

from .servers import HttpServerRunner


class TestHttpServerPing(unittest.TestCase):
    def test_ping_endpoint(self) -> None:
        """Test GET /ping returns 200 'pong'."""

        with HttpServerRunner(8087) as port:
            resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/ping')
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), b'pong')
            self.assertEqual(resp.headers.get('Content-Type'), 'text/plain; charset=utf-8')

    def test_not_found_endpoint(self) -> None:
        """Test unknown path returns 404 'not found'."""

        with HttpServerRunner(8087) as port:
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/unknown')
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)
                self.assertEqual(e.read(), b'not found')

    def test_root_path_not_found(self) -> None:
        """Test root path returns 404."""

        with HttpServerRunner(8087) as port:
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/')
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)

    def test_multiple_requests(self) -> None:
        """Test multiple sequential requests work."""

        with HttpServerRunner(8087) as port:
            # First request
            resp1 = urllib.request.urlopen(f'http://127.0.0.1:{port}/ping')
            self.assertEqual(resp1.status, 200)
            self.assertEqual(resp1.read(), b'pong')

            # Second request
            resp2 = urllib.request.urlopen(f'http://127.0.0.1:{port}/ping')
            self.assertEqual(resp2.status, 200)
            self.assertEqual(resp2.read(), b'pong')

            # Third request (404)
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/other')
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)

    def test_connection_closes_after_response(self) -> None:
        """Test that connection closes after response (Connection: close header)."""

        with HttpServerRunner(8087) as port:
            resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/ping')
            self.assertEqual(resp.headers.get('Connection'), 'close')
            resp.read()
