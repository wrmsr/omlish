# ruff: noqa: UP045
# @omlish-lite
import asyncio
import socket
import threading
import typing as ta
import unittest
import urllib.error
import urllib.request

from ...asyncio import AsyncioStreamChannelPipelineDriver
from .demos.http_server_ping import build_http_ping_channel


class TestHttpServerPing(unittest.TestCase):
    """
    Integration tests for the HTTP ping server.

    Tests spawn a real asyncio server in a separate thread and use urllib to make requests.
    """

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


class HttpServerRunner:
    """
    Context manager that runs an asyncio HTTP server in a background thread.

    Automatically finds an available port and shuts down cleanly on exit.
    """

    def __init__(self, preferred_port: int = 0) -> None:
        self._preferred_port = preferred_port
        self._port: ta.Optional[int] = None
        self._thread: ta.Optional[threading.Thread] = None
        self._loop: ta.Optional[asyncio.AbstractEventLoop] = None
        self._server: ta.Optional[asyncio.Server] = None
        self._ready = threading.Event()

    def __enter__(self) -> int:
        # Find available port
        self._port = self._find_available_port(self._preferred_port)

        # Start server in thread
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()

        # Wait for server to be ready
        if not self._ready.wait(timeout=5.0):
            raise RuntimeError('Server failed to start')

        return self._port

    def __exit__(self, *args: object) -> None:
        if self._loop is not None and self._server is not None:
            # Schedule shutdown on the event loop
            self._loop.call_soon_threadsafe(self._shutdown)

        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def _find_available_port(self, preferred: int) -> int:
        """Find an available port, trying preferred first."""

        if preferred:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', preferred))
                    return preferred
            except OSError:
                pass

        # Let OS assign a port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]

    def _run_server(self) -> None:
        """Run the asyncio server (runs in background thread)."""

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._serve())
        finally:
            self._loop.close()

    async def _serve(self) -> None:
        """Serve requests until shutdown."""

        async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            drv = AsyncioStreamChannelPipelineDriver(
                build_http_ping_channel(),
                reader,
                writer,
            )
            await drv.run()

        self._server = await asyncio.start_server(
            _handle_client,
            '127.0.0.1',
            self._port,
        )

        # Signal ready
        self._ready.set()

        # Serve until shutdown
        async with self._server:
            try:
                await self._server.serve_forever()
            except asyncio.CancelledError:
                # Expected when server is shutdown
                pass

    def _shutdown(self) -> None:
        """Shutdown the server (called from event loop thread)."""

        if self._server is not None:
            self._server.close()
