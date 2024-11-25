import select
import socket
import typing as ta

from omlish.lite.http.coroserver import CoroHttpServer
from omlish.lite.http.handlers import HttpHandler
from omlish.lite.http.handlers import HttpHandlerRequest
from omlish.lite.http.handlers import HttpHandlerResponse
from omlish.lite.io import DelimitingBuffer
from omlish.lite.socket import SocketAddress


class DelimitingReader:
    def __init__(self) -> None:
        super().__init__()
        self._lst: list[bytes] = []

    def feed(self, d: bytes) -> None:
        if d:
            self._lst.append(d)

    def _chop(self, i: int, e: int) -> bytes:
        lst = self._lst
        d = lst[i]

        o = b''.join([
            *lst[:i],
            d[:e],
        ])

        self._lst = [
            *([d[e:]] if e < len(d) else []),
            *lst[i + 1:],
        ]

        return o

    def read(self, n: int | None = None) -> bytes | None:
        if n is None:
            o = b''.join(self._lst)
            self._lst = []
            return o

        if not (lst := self._lst):
            return None

        c = 0
        for i, d in enumerate(lst):
            r = n - c
            if (l := len(d)) >= r:
                return self._chop(i, r)
            c += l

        return None

    def readline(self, delim: bytes = b'\n') -> bytes | None:
        if not (lst := self._lst):
            return None

        for i, d in enumerate(lst):
            if (p := d.find(delim)) >= 0:
                return self._chop(i, p + len(delim))

        return None


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
            io: IoManager,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._handler = handler
        self._io = io

        self._sock = socket.create_server(self._addr)
        self._sock.listen(1)

        io.register(self._on_conn, r=[self._sock.fileno()])

    def _on_conn(self) -> None:
        cli_sock, cli_addr = self._sock.accept()
        HttpServerConnection(
            cli_addr,
            cli_sock,
            self._handler,
            self._io,
        )


class HttpServerConnection:
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
            handler: HttpHandler,
            io: IoManager,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._sock = sock
        self._handler = handler
        self._io = io

        self._coro_srv = CoroHttpServer(
            addr,
            handler=self._handler,
        )
        self._srv_coro = self._coro_srv.coro_handle()
        self._cur_io = self._next_io(None)

        self._line_buf = DelimitingBuffer(keep_ends=True)

        io.register(self._on_read, r=[sock.fileno()])

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
                o = None
                break

            if isinstance(o, CoroHttpServer.AnyLogIo):
                print(o)
                continue

            break

        self._cur_io = o
        return o

    def _on_read(self) -> None:
        buf = self._sock.recv(1024)

        for out in self._line_buf.feed(buf):
            print(out)

        if not buf:
            self._io.unregister(r=[self._sock.fileno()])
            self._sock.close()
            return



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
    dr = DelimitingReader()
    dr.feed(b'abcd\nef')
    dr.feed(b'ghi\njkl')
    print(dr.read(5))
    print(dr.readline())
    print(dr.readline())


    iom = IoManager()

    srv_addr = ('localhost', 9999)
    HttpServer(
        srv_addr,
        say_hi_handler,
        iom,
    )

    while True:
        iom.poll()


if __name__ == '__main__':
    _main()
