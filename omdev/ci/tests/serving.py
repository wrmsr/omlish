# ruff: noqa: UP006 UP007
import contextlib
import ssl
import subprocess
import sys
import typing as ta

from omlish.docker.portrelay import DockerPortRelay
from omlish.http.coro.simple import make_simple_http_server
from omlish.http.handlers import HttpHandler
from omlish.http.handlers import LoggingHttpHandler
from omlish.lite.cached import cached_nullary
from omlish.lite.contextmanagers import AsyncExitStacked
from omlish.lite.logs import log
from omlish.secrets.tempssl import generate_temp_localhost_ssl_cert
from omlish.sockets.server.server import SocketServer


##


@contextlib.contextmanager
def start_docker_port_relay(
        docker_port: int,
        host_port: int,
        **kwargs: ta.Any,
) -> ta.Iterator[None]:
    with subprocess.Popen(DockerPortRelay(
            docker_port,
            host_port,
            **kwargs,
    ).run_cmd()) as proc:  # noqa
        yield


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
            es.enter_context(start_docker_port_relay(  # noqa
                relay_port,
                server_port,
                intermediate_port=server_port + 1,
            ))

        server.run()


##


class AsyncManagedSimpleHttpServer(AsyncExitStacked):
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
