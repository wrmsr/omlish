import abc
import select
import socket
import typing as ta

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_none
from omlish.lite.check import check_not_none
from omlish.lite.http.coroserver import CoroHttpServer
from omlish.lite.http.handlers import HttpHandler
from omlish.lite.http.handlers import HttpHandlerRequest
from omlish.lite.http.handlers import HttpHandlerResponse
from omlish.lite.io import IncrementalWriteBuffer
from omlish.lite.io import ReadableListBuffer
from omlish.lite.socket import SocketAddress


##


class IoDispatcher(abc.ABC):
    @abc.abstractmethod
    def fd(self) -> int:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def closed(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    #

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return False

    #

    def on_readable(self) -> None:
        raise TypeError

    def on_writable(self) -> None:
        raise TypeError


class SocketIoDispatcher(IoDispatcher, abc.ABC):
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._sock: ta.Optional[socket.socket] = sock

    def fd(self) -> int:
        return check_not_none(self._sock).fileno()

    @property
    def closed(self) -> bool:
        return self._sock is None

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close()
        self._sock = None


class IoManager:
    def __init__(self) -> None:
        super().__init__()

        self._ds: list[IoDispatcher] = []

    def register(self, d: IoDispatcher) -> None:
        self._ds.append(d)

    def poll(self, *, timeout: float = 1.) -> None:
        ds = self._ds
        rs = {d.fd(): d for d in ds if d.readable()}
        ws = {d.fd(): d for d in ds if d.writable()}

        print(f'rs={sorted(rs)}')
        print(f'ws={sorted(ws)}')
        print()

        ra, wa, _ = select.select(
            rs,
            ws,
            [],
            timeout,
        )

        print(f'ra={sorted(ra)}')
        print(f'wa={sorted(wa)}')
        print()

        for f in rs:
            rs[f].on_readable()
        for f in ws:
            ws[f].on_writable()


##


class HttpServer(SocketIoDispatcher):
    def __init__(
            self,
            addr: SocketAddress,
            handler: HttpHandler,
            io_mgr: IoManager,
    ) -> None:
        super().__init__(addr, socket.create_server(addr))

        self._handler = handler
        self._io_mgr = io_mgr

        sock = check_not_none(self._sock)
        sock.setblocking(False)
        sock.listen(1)

    def readable(self) -> bool:
        return True

    def _on_readable(self) -> None:
        cli_sock, cli_addr = self._sock.accept()

        conn = HttpServerConnection(
            cli_addr,
            cli_sock,
            self._handler,
            self._io_mgr,
        )

        self._io_mgr.register(conn)


class HttpServerConnection(SocketIoDispatcher):
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
            handler: HttpHandler,
            io_mgr: IoManager,
            *,
            read_size: int = 0x10,
            write_size: int = 0x10,
    ) -> None:
        super().__init__(addr, sock)

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

        sock = check_not_none(self._sock)
        sock.setblocking(False)

    #

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
                    self.close()
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
                break

            else:
                raise TypeError(o)

        self._cur_io = o
        return o

    #

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return self._write_buf is not None

    def on_readable(self) -> None:
        try:
            buf = self._sock.recv(self._read_size)
        except BlockingIOError:
            return
        except ConnectionResetError:
            self.close()
            return
        if not buf:
            self.close()
            return

        self._read_buf.feed(buf)

        if isinstance(self._cur_io, CoroHttpServer.AnyReadIo):
            self._next_io()

    def on_writable(self) -> None:
        check_isinstance(self._cur_io, CoroHttpServer.WriteIo)
        wb = check_not_none(self._write_buf)
        while wb.rem > 0:
            def send(d: bytes) -> int:
                try:
                    return self._sock.send(d)
                except ConnectionResetError:
                    self.close()
                    return 0
                except BlockingIOError:
                    return 0
            if not wb.write(send):
                break

        if wb.rem < 1:
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
