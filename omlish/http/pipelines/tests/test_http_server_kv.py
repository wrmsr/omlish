# ruff: noqa: S310 UP006 UP045
# @omlish-lite
# @omlish-precheck-allow-any-unicode
import typing as ta
import unittest
import urllib.error
import urllib.request

from .demos.http_server_kv import build_http_kv_channel
from .servers import HttpServerRunner


class TestHttpServerKv(unittest.TestCase):
    """Integration tests for the HTTP KV store server."""

    def test_post_and_get(self) -> None:
        """Test POST creates value and GET retrieves it."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            # POST a value
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/mykey',
                data=b'hello world',
                method='POST',
            )
            resp = urllib.request.urlopen(req)
            self.assertEqual(resp.status, 201)  # Created
            self.assertEqual(resp.read(), b'hello world')

            # GET the value back
            resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/mykey')
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), b'hello world')

    def test_put_updates_value(self) -> None:
        """Test PUT updates existing value."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            # POST initial value
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/key',
                data=b'value1',
                method='POST',
            )
            urllib.request.urlopen(req).read()

            # PUT new value
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/key',
                data=b'value2',
                method='PUT',
            )
            resp = urllib.request.urlopen(req)
            self.assertEqual(resp.status, 200)  # OK (not 201)
            self.assertEqual(resp.read(), b'value2')

            # GET to verify
            resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/key')
            self.assertEqual(resp.read(), b'value2')

    def test_get_nonexistent_key(self) -> None:
        """Test GET for nonexistent key returns 404."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/noexist')
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)
                self.assertEqual(e.read(), b'not found')

    def test_delete_key(self) -> None:
        """Test DELETE removes key."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            # POST a value
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/deleteme',
                data=b'temp',
                method='POST',
            )
            urllib.request.urlopen(req).read()

            # DELETE it
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/deleteme',
                method='DELETE',
            )
            resp = urllib.request.urlopen(req)
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), b'deleted')

            # Verify it's gone
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/deleteme')
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)

    def test_delete_nonexistent_key(self) -> None:
        """Test DELETE for nonexistent key returns 404."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/noexist',
                method='DELETE',
            )
            try:
                urllib.request.urlopen(req)
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 404)

    def test_multi_segment_path_rejected(self) -> None:
        """Test that paths with slashes are rejected."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/foo/bar',
                data=b'value',
                method='POST',
            )
            try:
                urllib.request.urlopen(req)
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 400)
                self.assertEqual(e.read(), b'bad request')

    def test_root_path_rejected(self) -> None:
        """Test that root path is rejected."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/')
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 400)

    def test_unsupported_method(self) -> None:
        """Test that unsupported methods return 405."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/key',
                method='PATCH',
            )
            try:
                urllib.request.urlopen(req)
                self.fail('Expected HTTPError')
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 405)
                self.assertEqual(e.read(), b'method not allowed')

    def test_multiple_keys(self) -> None:
        """Test storing multiple keys."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            # Store multiple keys
            for key, value in [('key1', 'value1'), ('key2', 'value2'), ('key3', 'value3')]:
                req = urllib.request.Request(
                    f'http://127.0.0.1:{port}/{key}',
                    data=value.encode(),
                    method='POST',
                )
                urllib.request.urlopen(req).read()

            # Verify all exist
            for key, expected in [('key1', 'value1'), ('key2', 'value2'), ('key3', 'value3')]:
                resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/{key}')
                self.assertEqual(resp.read(), expected.encode())

    def test_utf8_values(self) -> None:
        """Test storing UTF-8 values."""

        items: ta.Dict[str, str] = {}

        with HttpServerRunner(lambda: build_http_kv_channel(items), 8088, use_flow_control=True) as port:
            utf8_value = 'Hello 世界 🌍'.encode()

            req = urllib.request.Request(
                f'http://127.0.0.1:{port}/unicode',
                data=utf8_value,
                method='POST',
            )
            urllib.request.urlopen(req).read()

            resp = urllib.request.urlopen(f'http://127.0.0.1:{port}/unicode')
            self.assertEqual(resp.read(), utf8_value)
