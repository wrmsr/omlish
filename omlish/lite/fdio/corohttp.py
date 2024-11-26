import socket
import typing as ta

from ..check import check_isinstance
from ..check import check_none
from ..check import check_not_none
from ..check import check_state
from ..http.coroserver import CoroHttpServer
from ..http.handlers import HttpHandler
from ..io import IncrementalWriteBuffer
from ..io import ReadableListBuffer
from ..socket import SocketAddress
from .handlers import SocketFdIoHandler


class CoroHttpServerConnectionFdIoHandler(SocketFdIoHandler):
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
            handler: HttpHandler,
            *,
            read_size: int = 0x10000,
            write_size: int = 0x10000,
    ) -> None:
        check_state(not sock.getblocking())

        super().__init__(addr, sock)

        self._handler = handler
        self._read_size = read_size
        self._write_size = write_size

        self._read_buf = ReadableListBuffer()
        self._write_buf: IncrementalWriteBuffer | None = None

        self._coro_srv = CoroHttpServer(
            addr,
            handler=self._handler,
        )
        self._srv_coro: ta.Optional[ta.Generator[CoroHttpServer.Io, ta.Optional[bytes], None]] = self._coro_srv.coro_handle()  # noqa

        self._cur_io: CoroHttpServer.Io | None = None
        self._next_io()

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

    #

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return self._write_buf is not None

    #

    def on_readable(self) -> None:
        try:
            buf = check_not_none(self._sock).recv(self._read_size)
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
                    return check_not_none(self._sock).send(d)
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
