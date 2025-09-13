# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import socket
import typing as ta

from ....io.buffers import IncrementalWriteBuffer
from ....io.buffers import ReadableListBuffer
from ....io.fdio.handlers import SocketFdioHandler
from ....lite.check import check
from ....sockets.addresses import SocketAddress
from ...handlers import HttpHandler
from ..io import CoroHttpIo
from .server import CoroHttpServer


##


class CoroHttpServerConnectionFdioHandler(SocketFdioHandler):
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
            handler: HttpHandler,
            *,
            read_size: int = 0x10000,
            write_size: int = 0x10000,
            log_handler: ta.Optional[ta.Callable[[CoroHttpServer, CoroHttpIo.AnyLogIo], None]] = None,
    ) -> None:
        check.state(not sock.getblocking())

        super().__init__(addr, sock)

        self._handler = handler
        self._read_size = read_size
        self._write_size = write_size
        self._log_handler = log_handler

        self._read_buf = ReadableListBuffer()
        self._write_buf: ta.Optional[IncrementalWriteBuffer] = None

        self._coro_srv = CoroHttpServer(
            addr,
            handler=self._handler,
        )
        self._srv_coro: ta.Optional[
            ta.Generator[
                CoroHttpIo.Io,
                ta.Optional[bytes],
                CoroHttpServer.CoroHandleResult,
            ],
        ] = self._coro_srv.coro_handle()

        self._cur_io: ta.Optional[CoroHttpIo.Io] = None
        self._next_io()

    #

    def _next_io(self) -> None:  # noqa
        coro = check.not_none(self._srv_coro)

        d: ta.Optional[bytes] = None
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

            if isinstance(o, CoroHttpIo.AnyLogIo):
                if self._log_handler is not None:
                    self._log_handler(self._coro_srv, o)
                o = None

            elif isinstance(o, CoroHttpIo.ReadIo):
                if (d := self._read_buf.read(o.sz)) is None:
                    break
                o = None

            elif isinstance(o, CoroHttpIo.ReadLineIo):
                if (d := self._read_buf.read_until(b'\n')) is None:
                    break
                o = None

            elif isinstance(o, CoroHttpIo.WriteIo):
                check.none(self._write_buf)
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
            buf = check.not_none(self._sock).recv(self._read_size)
        except BlockingIOError:
            return
        except ConnectionResetError:
            self.close()
            return
        if not buf:
            self.close()
            return

        self._read_buf.feed(buf)

        if isinstance(self._cur_io, CoroHttpIo.AnyReadIo):
            self._next_io()

    def on_writable(self) -> None:
        check.isinstance(self._cur_io, CoroHttpIo.WriteIo)
        wb = check.not_none(self._write_buf)
        while wb.rem > 0:
            def send(d: bytes) -> int:
                try:
                    return check.not_none(self._sock).send(d)
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
