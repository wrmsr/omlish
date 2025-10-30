# @omlish-lite
# ruff: noqa: UP045
import errno
import socket
import typing as ta
import urllib.parse

from ....io.buffers import ReadableListBuffer
from ....lite.check import check
from ...coro.client.connection import CoroHttpClientConnection
from ...coro.client.response import CoroHttpClientResponse
from ...coro.io import CoroHttpIo
from ...headers import HttpHeaders
from ...urls import unparse_url_request_path
from ..base import HttpClientContext
from ..base import HttpClientError
from ..base import HttpRequest
from ..sync import HttpClient
from ..sync import StreamHttpResponse


T = ta.TypeVar('T')


##


class CoroHttpClient(HttpClient):
    class _Connection:
        def __init__(self, req: HttpRequest) -> None:
            super().__init__()

            self._req = req
            self._ups = urllib.parse.urlparse(req.url)

            self._ssl = self._ups.scheme == 'https'

        _cc: ta.Optional[CoroHttpClientConnection] = None
        _resp: ta.Optional[CoroHttpClientResponse] = None

        _sock: ta.Optional[socket.socket] = None
        _sock_file: ta.Optional[ta.BinaryIO] = None

        _ssl_context: ta.Any = None

        #

        def _create_https_context(self, http_version: int) -> ta.Any:
            # https://github.com/python/cpython/blob/a7160912274003672dc116d918260c0a81551c21/Lib/http/client.py#L809
            import ssl

            # Function also used by urllib.request to be able to set the check_hostname attribute on a context object.
            context = ssl.create_default_context()

            # Send ALPN extension to indicate HTTP/1.1 protocol.
            if http_version == 11:
                context.set_alpn_protocols(['http/1.1'])

            # Enable PHA for TLS 1.3 connections if available.
            if context.post_handshake_auth is not None:
                context.post_handshake_auth = True

            return context

        #

        def setup(self) -> StreamHttpResponse:
            check.none(self._sock)
            check.none(self._ssl_context)

            self._cc = cc = CoroHttpClientConnection(
                check.not_none(self._ups.hostname),
                default_port=CoroHttpClientConnection.HTTPS_PORT if self._ssl else CoroHttpClientConnection.HTTP_PORT,
            )

            if self._ssl:
                self._ssl_context = self._create_https_context(self._cc.http_version)

            try:
                self._run_coro(cc.connect())

                self._run_coro(cc.request(
                    self._req.method or 'GET',
                    unparse_url_request_path(self._ups) or '/',
                    self._req.data,
                    hh.single_str_dct if (hh := self._req.headers_) is not None else {},
                ))

                self._resp = resp = self._run_coro(cc.get_response())

                return StreamHttpResponse(
                    status=resp._state.status,  # noqa
                    headers=HttpHeaders(resp._state.headers.items()),  # noqa
                    request=self._req,
                    underlying=self,
                    _stream=ReadableListBuffer().new_buffered_reader(self),
                    _closer=self.close,
                )

            except Exception:
                self.close()
                raise

        def _run_coro(self, g: ta.Generator[ta.Any, ta.Any, T]) -> T:
            i = None

            while True:
                try:
                    o = g.send(i)
                except StopIteration as e:
                    return e.value

                try:
                    i = self._handle_io(o)
                except OSError as e:
                    raise HttpClientError from e

        def _handle_io(self, o: CoroHttpIo.Io) -> ta.Any:
            if isinstance(o, CoroHttpIo.ConnectIo):
                check.none(self._sock)
                self._sock = socket.create_connection(*o.args, **(o.kwargs or {}))

                if self._ssl_context is not None:
                    self._sock = self._ssl_context.wrap_socket(
                        self._sock,
                        server_hostname=check.not_none(o.server_hostname),
                    )

                # Might fail in OSs that don't implement TCP_NODELAY
                try:
                    self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                except OSError as e:
                    if e.errno != errno.ENOPROTOOPT:
                        raise

                self._sock_file = self._sock.makefile('rb')

                return None

            elif isinstance(o, CoroHttpIo.CloseIo):
                check.not_none(self._sock).close()
                return None

            elif isinstance(o, CoroHttpIo.WriteIo):
                check.not_none(self._sock).sendall(o.data)
                return None

            elif isinstance(o, CoroHttpIo.ReadIo):
                if (sz := o.sz) is not None:
                    return check.not_none(self._sock_file).read(sz)
                else:
                    return check.not_none(self._sock_file).read()

            elif isinstance(o, CoroHttpIo.ReadLineIo):
                return check.not_none(self._sock_file).readline(o.sz)

            else:
                raise TypeError(o)

        def read1(self, n: int = -1, /) -> bytes:
            return self._run_coro(check.not_none(self._resp).read(n if n >= 0 else None))

        def close(self) -> None:
            if self._resp is not None:
                self._resp.close()
            if self._sock is not None:
                self._sock.close()

    def _stream_request(self, ctx: HttpClientContext, req: HttpRequest) -> StreamHttpResponse:
        conn = CoroHttpClient._Connection(req)
        return conn.setup()
