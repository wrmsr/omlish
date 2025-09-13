# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import itertools
import typing as ta

from ....lite.check import check
from ....sockets.addresses import SocketAddress
from ....sockets.handlers import SocketHandler_
from ....sockets.io import SocketIoPair
from ..io import CoroHttpIo
from .server import CoroHttpServer
from .server import CoroHttpServerFactory


##


class CoroHttpServerSocketHandler(SocketHandler_):
    def __init__(
            self,
            server_factory: CoroHttpServerFactory,
            *,
            keep_alive: bool = False,
            log_handler: ta.Optional[ta.Callable[[CoroHttpServer, CoroHttpIo.AnyLogIo], None]] = None,
    ) -> None:
        super().__init__()

        self._server_factory = server_factory
        self._keep_alive = keep_alive
        self._log_handler = log_handler

    def __call__(self, client_address: SocketAddress, fp: SocketIoPair) -> None:
        server = self._server_factory(client_address)

        if self._keep_alive:
            for i in itertools.count():  # noqa
                res = self._handle_one(server, fp)
                if res.close_reason is not None:
                    break

        else:
            self._handle_one(server, fp)

    def _handle_one(
            self,
            server: CoroHttpServer,
            fp: SocketIoPair,
    ) -> CoroHttpServer.CoroHandleResult:
        gen = server.coro_handle()

        o = next(gen)
        while True:
            if isinstance(o, CoroHttpIo.AnyLogIo):
                i = None
                if self._log_handler is not None:
                    self._log_handler(server, o)

            elif isinstance(o, CoroHttpIo.ReadIo):
                i = fp.r.read(check.not_none(o.sz))

            elif isinstance(o, CoroHttpIo.ReadLineIo):
                i = fp.r.readline(o.sz)

            elif isinstance(o, CoroHttpIo.WriteIo):
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
            except StopIteration as e:
                return check.isinstance(e.value, CoroHttpServer.CoroHandleResult)
