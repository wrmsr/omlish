# ruff: noqa: UP006 UP007
import asyncio
import contextlib
import logging
import ssl
import sys
import threading
import typing as ta

from omlish.docker.ports import DockerPortRelay
from omlish.http.coro.simple import make_simple_http_server
from omlish.http.handlers import HttpHandler
from omlish.http.handlers import LoggingHttpHandler
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import AsyncExitStacked
from omlish.secrets.tempssl import generate_temp_localhost_ssl_cert
from omlish.sockets.server.server import SocketServer

from ...dataserver.http import DataServerHttpHandler
from ...dataserver.server import DataServer


##


@contextlib.asynccontextmanager
async def start_docker_port_relay(
        docker_port: int,
        host_port: int,
        **kwargs: ta.Any,
) -> ta.AsyncGenerator[None, None]:
    proc = await asyncio.create_subprocess_exec(*DockerPortRelay(
        docker_port,
        host_port,
        **kwargs,
    ).run_cmd())

    try:
        yield

    finally:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        await proc.wait()


##


class AsyncioManagedSimpleHttpServer(AsyncExitStacked):
    def __init__(
            self,
            port: int,
            handler: HttpHandler,
            *,
            temp_ssl: bool = False,
    ) -> None:
        super().__init__()

        self._port = port
        self._handler = handler

        self._temp_ssl = temp_ssl

        self._lock = threading.RLock()

        self._loop: ta.Optional[asyncio.AbstractEventLoop] = None
        self._thread: ta.Optional[threading.Thread] = None
        self._thread_exit_event = asyncio.Event()
        self._server: ta.Optional[SocketServer] = None

    @cached_nullary
    def _ssl_context(self) -> ta.Optional['ssl.SSLContext']:
        if not self._temp_ssl:
            return None

        ssl_cert = generate_temp_localhost_ssl_cert().cert  # FIXME: async blocking

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            keyfile=ssl_cert.key_file,
            certfile=ssl_cert.cert_file,
        )

        return ssl_context

    @contextlib.contextmanager
    def _make_server(self) -> ta.Iterator[SocketServer]:
        with make_simple_http_server(
                self._port,
                self._handler,
                ssl_context=self._ssl_context(),
                ignore_ssl_errors=True,
                use_threads=True,
        ) as server:
            yield server

    def _thread_main(self) -> None:
        try:
            check.none(self._server)
            with self._make_server() as server:
                self._server = server

                server.run()

        finally:
            check.not_none(self._loop).call_soon_threadsafe(self._thread_exit_event.set)

    def is_running(self) -> bool:
        return self._server is not None

    def shutdown(self) -> None:
        if (server := self._server) is not None:
            server.shutdown(block=False)

    async def run(self) -> None:
        with self._lock:
            check.none(self._loop)
            check.none(self._thread)
            check.state(not self._thread_exit_event.is_set())

            if self._temp_ssl:
                # Hit the ExitStack from this thread
                self._ssl_context()

            self._loop = check.not_none(asyncio.get_running_loop())
            self._thread = threading.Thread(
                target=self._thread_main,
                daemon=True,
            )
            self._thread.start()

        await self._thread_exit_event.wait()


##


class DockerDataServer(AsyncExitStacked):
    def __init__(
            self,
            port: int,
            data_server: DataServer,
            *,
            handler_log: ta.Optional[logging.Logger] = None,
            stop_event: ta.Optional[asyncio.Event] = None,
    ) -> None:
        super().__init__()

        self._port = port
        self._data_server = data_server

        self._handler_log = handler_log

        if stop_event is None:
            stop_event = asyncio.Event()
        self._stop_event = stop_event

    @property
    def stop_event(self) -> asyncio.Event:
        return self._stop_event

    async def run(self) -> None:
        # FIXME:
        #  - shared single server with updatable routes
        #  - get docker used ports with ns1
        #  - discover server port with get_available_port
        #  - discover relay port pair with get_available_ports
        # relay_port: ta.Optional[ta.Tuple[int, int]] = None

        relay_port: ta.Optional[int] = None
        if sys.platform == 'darwin':
            relay_port = self._port
            server_port = self._port + 1
        else:
            server_port = self._port

        #

        handler: HttpHandler = DataServerHttpHandler(self._data_server)

        if self._handler_log is not None:
            handler = LoggingHttpHandler(
                handler,
                self._handler_log,
            )

        #

        async with contextlib.AsyncExitStack() as es:
            if relay_port is not None:
                await es.enter_async_context(start_docker_port_relay(  # noqa
                    relay_port,
                    server_port,
                    intermediate_port=server_port + 1,
                ))

            async with AsyncioManagedSimpleHttpServer(
                    server_port,
                    handler,
                    temp_ssl=True,
            ) as server:
                server_run_task = asyncio.create_task(server.run())
                try:
                    await self._stop_event.wait()

                finally:
                    server.shutdown()
                    await server_run_task
