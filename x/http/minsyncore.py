import select
import socket
import typing as ta

from omlish.lite.check import check_none
from omlish.lite.check import check_not_none
from omlish.lite.check import check_state
from omlish.lite.http.coroserver import CoroHttpServer
from omlish.lite.http.handlers import HttpHandler
from omlish.lite.http.handlers import HttpHandlerRequest
from omlish.lite.http.handlers import HttpHandlerResponse
from omlish.lite.io import ReadableListBuffer
from omlish.lite.socket import SocketAddress


class IoManager:
    def __init__(self) -> None:
        super().__init__()

        self._read_callbacks: dict[int, ta.Callable[[], None]] = {}
        self._write_callbacks: dict[int, ta.Callable[[], None]] = {}

    def unregister(
            self,
            *,
            r: ta.Iterable[int] = (),
            w: ta.Iterable[int] = (),
    ) -> None:
        for f in r:
            del self._read_callbacks[f]
        for f in w:
            del self._write_callbacks[f]

    def register(
            self,
            fn: ta.Callable[[], None],
            *,
            r: ta.Iterable[int] = (),
            w: ta.Iterable[int] = (),
    ) -> None:
        for f in r:
            self._read_callbacks[f] = fn
        for f in w:
            self._write_callbacks[f] = fn

    def poll(self, *, timeout: float = 1.) -> None:
        print(f'rd={sorted(self._read_callbacks)}')
        print(f'wd={sorted(self._read_callbacks)}')
        print()

        readable, writable, _ = select.select(
            self._read_callbacks,
            self._write_callbacks,
            [],
            timeout,
        )

        print(f'rl={sorted(readable)}')
        print(f'wl={sorted(writable)}')
        print()

        for rf in readable:
            self._read_callbacks[rf]()
        for wf in writable:
            self._write_callbacks[wf]()


class HttpServer:
    def __init__(
            self,
            addr: SocketAddress,
            handler: HttpHandler,
            io_mgr: IoManager,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._handler = handler
        self._io_mgr = io_mgr

        self._sock = sock = socket.create_server(self._addr)
        sock.setblocking(False)
        sock.listen(1)
        io_mgr.register(self._on_readable, r=[self._sock.fileno()])

    def _on_readable(self) -> None:
        cli_sock, cli_addr = self._sock.accept()

        HttpServerConnection(
            cli_addr,
            cli_sock,
            self._handler,
            self._io_mgr,
        )


class HttpServerConnection:
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
            handler: HttpHandler,
            io_mgr: IoManager,
            *,
            read_size: int = 0x10000,
            write_size: int = 0x10000,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._sock = sock
        self._handler = handler
        self._io_mgr = io_mgr
        self._read_size = read_size
        self._write_size = write_size

        self._coro_srv = CoroHttpServer(
            addr,
            handler=self._handler,
        )
        self._srv_coro = self._coro_srv.coro_handle()
        self._cur_io = self._next_io(None)

        self._read_buf = ReadableListBuffer()
        self._write_bufs: list[bytes] | None = None

        sock.setblocking(False)
        io_mgr.register(self._on_readable, r=[sock.fileno()])

    def _next_io(self, d: bytes | None) -> CoroHttpServer.Io | None:  # noqa
        o: CoroHttpServer.Io | None
        while True:
            try:
                if d is not None:
                    o = self._srv_coro.send(d)
                    d = None
                else:
                    o = next(self._srv_coro)
            except StopIteration:
                self._close()
                o = None
                break

            if isinstance(o, CoroHttpServer.AnyLogIo):
                print(o)
                continue

            elif isinstance(o, CoroHttpServer.WriteIo):
                check_state(bool(o.data))
                check_none(self._write_bufs)
                self._write_bufs = [
                    o.data[i:i + self._write_size]
                    for i in range(0, len(o.data), self._write_size)
                ]
                self._io_mgr.register(self._on_writable, w=[self._sock.fileno()])
                break

            break

        self._cur_io = o
        return o

    def _close(self) -> None:
        self._io_mgr.unregister(
            r=[self._sock.fileno()],
            w=[self._sock.fileno()] if self._write_bufs else [],
        )
        self._sock.close()

    def _on_readable(self) -> None:
        try:
            buf = self._sock.recv(self._read_size)
        except BlockingIOError:
            return
        except ConnectionResetError:
            self._close()
            return
        if not buf:
            self._close()
            return

        self._read_buf.feed(buf)

        ci = self._cur_io
        while True:
            if isinstance(ci, CoroHttpServer.ReadIo):
                if (d := self._read_buf.read(ci.sz)) is None:
                    break
                self._next_io(d)
            elif isinstance(ci, CoroHttpServer.ReadLineIo):
                if (d := self._read_buf.read_until(b'\n')) is None:
                    break
                self._next_io(d)
            else:
                break

    def _on_writable(self) -> None:
        check_state(bool(lst := self._write_bufs))

        t = 0
        for i, d in enumerate(lst):
            check_state(bool(d))
            try:
                n = self._sock.send(d)
            except ConnectionResetError:
                self._close()
                return
            except BlockingIOError:
                n = 0
                break
            t += n

        if not t:
            return

        nwb = [
            *([d[n:]] if n < len(d) else []),
            *lst[i + 1:],
        ]

        if not nwb:
            self._write_bufs = None
            self._io_mgr.unregister(w=[self._sock.fileno()])
            self._next_io(None)
        else:
            self._write_size = nwb


def say_hi_handler(req: HttpHandlerRequest) -> HttpHandlerResponse:
    resp = '\n'.join([
        f'method: {req.method}',
        f'path: {req.path}',
        f'data: {len(req.data or b"")}',
        '',
    ])

    return HttpHandlerResponse(
        200,
        data=resp.encode('utf-8'),
    )


def _main() -> None:
    io_mgr = IoManager()

    srv_addr = ('localhost', 9999)
    HttpServer(
        srv_addr,
        say_hi_handler,
        io_mgr,
    )

    while True:
        io_mgr.poll()


if __name__ == '__main__':
    _main()
