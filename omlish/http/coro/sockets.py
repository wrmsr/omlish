# ruff: noqa: UP006 UP007
# @omlish-lite
import typing as ta

from ...sockets.addresses import SocketAddress
from ...sockets.handlers import SocketHandler_
from ...sockets.io import SocketIoPair
from .server import CoroHttpServer
from .server import CoroHttpServerFactory


##


class CoroHttpServerSocketHandler(SocketHandler_):
    def __init__(
            self,
            server_factory: CoroHttpServerFactory,
            *,
            log_handler: ta.Optional[ta.Callable[[CoroHttpServer, CoroHttpServer.AnyLogIo], None]] = None,
    ) -> None:
        super().__init__()

        self._server_factory = server_factory
        self._log_handler = log_handler

    def __call__(self, client_address: SocketAddress, fp: SocketIoPair) -> None:
        server = self._server_factory(client_address)

        gen = server.coro_handle()

        o = next(gen)
        while True:
            if isinstance(o, CoroHttpServer.AnyLogIo):
                i = None
                if self._log_handler is not None:
                    self._log_handler(server, o)

            elif isinstance(o, CoroHttpServer.ReadIo):
                i = fp.r.read(o.sz)

            elif isinstance(o, CoroHttpServer.ReadLineIo):
                i = fp.r.readline(o.sz)

            elif isinstance(o, CoroHttpServer.WriteIo):
                i = None
                fp.w.write(o.data)
                fp.w.flush()

            else:
                raise TypeError(o)

            try:
                if i is not None:
                    o = gen.send(i)
                else:
                    o = next(gen)
            except StopIteration:
                break
