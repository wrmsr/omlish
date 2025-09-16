# ruff: noqa: UP045
import errno
import socket
import typing as ta
import urllib.parse

from .....lite.check import check
from ....clients import HttpRequest
from ....clients import StreamHttpResponse
from ....clients.base import HttpClient
from ....headers import HttpHeaders
from ...io import CoroHttpIo
from ..client import CoroHttpClientConnection
from ..response import CoroHttpClientResponse


T = ta.TypeVar('T')


##


class CoroHttpClientHttpClient(HttpClient):
    class _Connection:
        def __init__(self, req: HttpRequest) -> None:
            super().__init__()

            self._req = req
            self._ups = urllib.parse.urlparse(req.url)

        _cc: CoroHttpClientConnection
        _resp: CoroHttpClientResponse

        _sock: ta.Optional[socket.socket] = None
        _sock_file: ta.Optional[ta.BinaryIO] = None

        def setup(self) -> StreamHttpResponse:
            self._cc = CoroHttpClientConnection(check.not_none(self._ups.hostname))
            self._run_coro(self._cc.connect())
            self._run_coro(self._cc.request('GET', self._ups.path or '/'))
            self._resp = self._run_coro(self._cc.get_response())
            return StreamHttpResponse(
                status=self._resp._state.status,  # noqa
                headers=HttpHeaders(self._resp._state.headers.items()),  # noqa
                request=self._req,
                underlying=self,
                stream=self,
                _closer=self.close,
            )

        def _run_coro(self, g: ta.Generator[ta.Any, ta.Any, T]) -> T:
            i = None
            while True:
                try:
                    o = g.send(i)
                except StopIteration as e:
                    return e.value
                i = self._handle_io(o)

        def _handle_io(self, o: CoroHttpIo.Io) -> ta.Any:
            if isinstance(o, CoroHttpIo.ConnectIo):
                check.none(self._sock)
                self._sock = socket.create_connection(*o.args, **(o.kwargs or {}))

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

        def read(self, /, n: int = -1) -> bytes:
            # return self._handle_io(self._cc.get_response())
            raise NotImplementedError

        def close(self) -> None:
            raise NotImplementedError

    def _stream_request(self, req: HttpRequest) -> StreamHttpResponse:
        conn = CoroHttpClientHttpClient._Connection(req)
        return conn.setup()
