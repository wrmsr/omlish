# ruff: noqa: UP006 UP007
import contextlib
import json
import socket
import typing as ta

from omlish.lite.check import check_not_none
from omlish.lite.contextmanagers import defer
from omlish.lite.fdio.corohttp import CoroHttpServerConnectionFdIoHandler
from omlish.lite.fdio.handlers import SocketFdIoHandler
from omlish.lite.http.handlers import HttpHandler
from omlish.lite.http.handlers import HttpHandlerRequest
from omlish.lite.http.handlers import HttpHandlerResponse
from omlish.lite.json import JSON_PRETTY_KWARGS
from omlish.lite.socket import SocketAddress

from .dispatchers import Dispatchers
from .groups import ProcessGroupManager
from .types import HasDispatchers


##


class SocketServerFdIoHandler(SocketFdIoHandler):
    def __init__(
            self,
            addr: SocketAddress,
            on_connect: ta.Callable[[socket.socket, SocketAddress], None],
    ) -> None:
        sock = socket.create_server(addr)
        sock.setblocking(False)

        super().__init__(addr, sock)

        self._on_connect = on_connect

        sock.listen(1)

    def readable(self) -> bool:
        return True

    def on_readable(self) -> None:
        cli_sock, cli_addr = check_not_none(self._sock).accept()
        cli_sock.setblocking(False)

        self._on_connect(cli_sock, cli_addr)


##


class HttpServer(HasDispatchers):
    class Address(ta.NamedTuple):
        a: SocketAddress

    class Handler(ta.NamedTuple):
        h: HttpHandler

    def __init__(
            self,
            handler: Handler,
            addr: Address = Address(('localhost', 8000)),
            *,
            exit_stack: contextlib.ExitStack,
    ) -> None:
        super().__init__()

        self._handler = handler.h
        self._addr = addr.a

        self._server = SocketServerFdIoHandler(self._addr, self._on_connect)

        self._conns: ta.List[CoroHttpServerConnectionFdIoHandler] = []

        exit_stack.enter_context(defer(self._server.close))  # noqa

    def get_dispatchers(self) -> Dispatchers:
        l = []
        for c in self._conns:
            if not c.closed:
                l.append(c)
        self._conns = l
        return Dispatchers([
            self._server,
            *l,
        ])

    def _on_connect(self, sock: socket.socket, addr: SocketAddress) -> None:
        conn = CoroHttpServerConnectionFdIoHandler(
            addr,
            sock,
            self._handler,
        )

        self._conns.append(conn)


##


class SupervisorHttpHandler:
    def __init__(
            self,
            *,
            groups: ProcessGroupManager,
    ) -> None:
        super().__init__()

        self._groups = groups

    def handle(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        dct = {
            'method': req.method,
            'path': req.path,
            'data': len(req.data or b''),
            'groups': {
                g.name: {
                    'processes': {
                        p.name: {
                            'pid': p.pid,
                            'state': p.state.name,
                        }
                        for p in g
                    },
                }
                for g in self._groups
            },
        }

        return HttpHandlerResponse(
            200,
            data=json.dumps(dct, **JSON_PRETTY_KWARGS).encode('utf-8') + b'\n',
            headers={
                'Content-Type': 'application/json',
            },
        )
