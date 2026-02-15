# ruff: noqa: S310 S324 UP045
# @omlish-lite
import hashlib
import unittest
import urllib.error
import urllib.request

from .demos.http_server_sha1 import build_http_sha1_channel
from .servers import HttpServerRunner


class TestHttpServerSha1(unittest.TestCase):
    """
    Integration tests for the HTTP SHA1 server.

    Tests streaming request body processing with incremental hash computation.
    """

    def test_sha1_small_body(self) -> None:
        """Test SHA1 computation with small body."""

        with HttpServerRunner(build_http_sha1_channel, 8090, use_flow_control=True) as port:
            data = b'hello world'
            expected_hash = hashlib.sha1(data).hexdigest().encode('ascii')

            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/sha1',
                data=data,
                method='POST',
            )
            resp = urllib.request.urlopen(req)

            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), expected_hash)

    def test_sha1_empty_body(self) -> None:
        """Test SHA1 computation with empty body."""

        with HttpServerRunner(build_http_sha1_channel, 8090, use_flow_control=True) as port:
            data = b''
            expected_hash = hashlib.sha1(data).hexdigest().encode('ascii')

            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/sha1',
                data=data,
                method='POST',
            )
            resp = urllib.request.urlopen(req)

            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), expected_hash)

    def test_sha1_large_body(self) -> None:
        """Test SHA1 computation with larger body (streaming)."""

        with HttpServerRunner(build_http_sha1_channel, 8090, use_flow_control=True) as port:
            # 1MB of data
            data = b'x' * (1024 * 1024)
            expected_hash = hashlib.sha1(data).hexdigest().encode('ascii')

            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/sha1',
                data=data,
                method='POST',
            )
            resp = urllib.request.urlopen(req)

            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), expected_hash)

    def test_sha1_binary_data(self) -> None:
        """Test SHA1 computation with binary data."""

        with HttpServerRunner(build_http_sha1_channel, 8090, use_flow_control=True) as port:
            # Binary data with all byte values
            data = bytes(range(256)) * 100
            expected_hash = hashlib.sha1(data).hexdigest().encode('ascii')

            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/sha1',
                data=data,
                method='POST',
            )
            resp = urllib.request.urlopen(req)

            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), expected_hash)

    def test_not_found_for_non_sha1_endpoint(self) -> None:
        """Test that non-/sha1 paths return 404."""

        with HttpServerRunner(build_http_sha1_channel, 8090, use_flow_control=True) as port:
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/other',
                data=b'data',
                method='POST',
            )
            try:
                urllib.request.urlopen(req)
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)
                self.assertEqual(e.read(), b'not found')

    def test_not_found_for_get_request(self) -> None:
        """Test that GET requests return 404."""

        with HttpServerRunner(build_http_sha1_channel, 8090, use_flow_control=True) as port:
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/sha1')
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)

    def test_multiple_requests(self) -> None:
        """Test multiple sequential SHA1 requests."""

        with HttpServerRunner(build_http_sha1_channel, 8090, use_flow_control=True) as port:
            test_data = [
                b'first',
                b'second',
                b'third',
            ]

            for data in test_data:
                expected_hash = hashlib.sha1(data).hexdigest().encode('ascii')

                req = urllib.request.Request(
                    f'http://127.0.0.1:{port}/sha1',
                    data=data,
                    method='POST',
                )
                resp = urllib.request.urlopen(req)

                self.assertEqual(resp.status, 200)
                self.assertEqual(resp.read(), expected_hash)

    def test_connection_closes_after_response(self) -> None:
        """Test that connection closes after response."""

        with HttpServerRunner(build_http_sha1_channel, 8090, use_flow_control=True) as port:
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/sha1',
                data=b'test',
                method='POST',
            )
            resp = urllib.request.urlopen(req)
            self.assertEqual(resp.headers.get('Connection'), 'close')
            resp.read()
