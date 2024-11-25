import select
import socket
import typing as ta

from omlish.lite.check import check_none
from omlish.lite.check import check_not_none
from omlish.lite.check import check_isinstance
from omlish.lite.check import check_non_empty
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


class IncrementalWriteBuffer:
    def __init__(
            self,
            data: bytes,
            *,
            write_size: int = 0x10000,
    ) -> None:
        super().__init__()

        check_non_empty(data)
        self._len = len(data)
        self._write_size = write_size

        self._lst = [
            data[i:i + write_size]
            for i in range(0, len(data), write_size)
        ]
        self._pos = 0

    @property
    def rem(self) -> int:
        return self._len - self._pos

    def write(self, fn: ta.Callable[[bytes], int]) -> int:
        lst = check_non_empty(self._lst)

        t = 0
        for i, d in enumerate(lst):
            n = fn(check_non_empty(d))
            if not n:
                break
            t += n

        if t:
            self._lst = [
                *([d[n:]] if n < len(d) else []),
                *lst[i + 1:],
            ]
            self._pos += t

        return t



class HttpServerConnection:
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
            handler: HttpHandler,
            io_mgr: IoManager,
            *,
            read_size: int = 0x100,
            write_size: int = 0x100,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._sock = sock
        self._handler = handler
        self._io_mgr = io_mgr
        self._read_size = read_size
        self._write_size = write_size

        self._read_buf = ReadableListBuffer()
        self._write_buf: IncrementalWriteBuffer | None = None

        self._coro_srv = CoroHttpServer(
            addr,
            handler=self._handler,
        )
        self._srv_coro: ta.Generator[CoroHttpServer.Io, ta.Optional[bytes], None] | None = self._coro_srv.coro_handle()
        self._cur_io: CoroHttpServer.Io | None = None
        self._next_io()

        sock.setblocking(False)
        io_mgr.register(self._on_readable, r=[sock.fileno()])

    def _next_io(self) -> None:  # noqa
        coro = check_not_none(self._srv_coro)

        d: bytes | None = None
        o = self._cur_io
        while True:
            if o is None:
                try:
                    if d is not None:
                        o = coro.send(d)
                        d = None
                    else:
                        o = next(coro)
                except StopIteration:
                    self._close()
                    o = None
                    break

            if isinstance(o, CoroHttpServer.AnyLogIo):
                print(o)
                o = None

            elif isinstance(o, CoroHttpServer.ReadIo):
                if (d := self._read_buf.read(o.sz)) is None:
                    break
                o = None

            elif isinstance(o, CoroHttpServer.ReadLineIo):
                if (d := self._read_buf.read_until(b'\n')) is None:
                    break
                o = None

            elif isinstance(o, CoroHttpServer.WriteIo):
                check_none(self._write_buf)
                self._write_buf = IncrementalWriteBuffer(o.data, write_size=self._write_size)
                self._io_mgr.register(self._on_writable, w=[self._sock.fileno()])
                break

            else:
                raise TypeError(o)

        self._cur_io = o
        return o

    def _close(self) -> None:
        self._io_mgr.unregister(
            r=[self._sock.fileno()],
            w=[self._sock.fileno()] if self._write_buf is not None else [],
        )
        self._sock.close()
        self._srv_coro = None

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

        if isinstance(self._cur_io, CoroHttpServer.AnyReadIo):
            self._next_io()

    def _on_writable(self) -> None:
        check_isinstance(self._cur_io, CoroHttpServer.WriteIo)
        wb = check_not_none(self._write_buf)
        while wb.rem > 0:
            def send(d: bytes) -> int:
                try:
                    return self._sock.send(d)
                except ConnectionResetError:
                    self._close()
                    return 0
                except BlockingIOError:
                    return 0
            if not wb.write(send):
                break

        if wb.rem < 1:
            self._io_mgr.unregister(w=[self._sock.fileno()])
            self._write_buf = None
            self._cur_io = None
            self._next_io()


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

    srv_addr = ('localhost', 8000)
    HttpServer(
        srv_addr,
        say_hi_handler,
        io_mgr,
    )

    while True:
        io_mgr.poll()


if __name__ == '__main__':
    _main()
