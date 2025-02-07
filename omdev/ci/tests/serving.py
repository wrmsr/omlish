# ruff: noqa: UP006 UP007
import asyncio
import contextlib
import ssl
import subprocess
import sys
import threading
import typing as ta

from omlish.docker.portrelay import DockerPortRelay
from omlish.http.coro.simple import make_simple_http_server
from omlish.http.handlers import HttpHandler
from omlish.http.handlers import LoggingHttpHandler
from omlish.http.handlers import StringResponseHttpHandler
from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.contextmanagers import AsyncExitStacked
from omlish.lite.logs import log
from omlish.secrets.tempssl import generate_temp_localhost_ssl_cert
from omlish.sockets.server.server import SocketServer


##


@contextlib.asynccontextmanager
async def start_docker_port_relay(
        docker_port: int,
        host_port: int,
        **kwargs: ta.Any,
) -> ta.Iterator[None]:
    proc = await asyncio.create_subprocess_exec(
            *DockerPortRelay(
                docker_port,
                host_port,
                **kwargs,
            ).run_cmd()
    )

    try:
        yield

    finally:
        proc.kill()
        await proc.wait()


##


def serve_for_docker(
        port: int,
        handler: HttpHandler,
        *,
        temp_ssl: bool = False,
) -> None:
    relay_port: ta.Optional[int] = None
    if sys.platform == 'darwin':
        relay_port = port
        server_port = port + 1
    else:
        server_port = port

    ssl_context: ta.Optional[ssl.SSLContext] = None
    if temp_ssl:
        ssl_cert = generate_temp_localhost_ssl_cert().cert

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            keyfile=ssl_cert.key_file,
            certfile=ssl_cert.cert_file,
        )

    with contextlib.ExitStack() as es:
        server: SocketServer = es.enter_context(make_simple_http_server(  # noqa
            server_port,
            LoggingHttpHandler(handler, log),
            ssl_context=ssl_context,
            use_threads=True,
        ))

        if relay_port is not None:
            es.enter_context(subprocess.Popen(DockerPortRelay(
                relay_port,
                server_port,
                intermediate_port=server_port + 1,
            ).run_cmd()))

        server.run()


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


async def _a_main() -> None:
    port = 5021

    relay_port: ta.Optional[int] = None
    if sys.platform == 'darwin':
        relay_port = port
        server_port = port + 1
    else:
        server_port = port

    async with start_docker_port_relay(
            relay_port,
            server_port,
            intermediate_port=server_port + 1,
    ):
        async with AsyncioManagedSimpleHttpServer(
                server_port,
                StringResponseHttpHandler('hi'),
                temp_ssl=True,
        ) as server:
            server_run_task = asyncio.create_task(server.run())
            try:
                await asyncio.sleep(10.)
            finally:
                server.shutdown()
                await server_run_task


if __name__ == '__main__':
    asyncio.run(_a_main())
