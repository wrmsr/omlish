# ruff: noqa: UP006 UP007 UP045
import contextlib
import json
import socket
import typing as ta

from omlish.http.coro.server.fdio import CoroHttpServerConnectionFdioHandler
from omlish.http.simple.handlers import SimpleHttpHandler
from omlish.http.simple.handlers import SimpleHttpHandler_
from omlish.http.simple.handlers import SimpleHttpHandlerRequest
from omlish.http.simple.handlers import SimpleHttpHandlerResponse
from omlish.io.fdio.handlers import ServerSocketFdioHandler
from omlish.lite.json import JSON_PRETTY_KWARGS
from omlish.sockets.addresses import SocketAddress

from .dispatchers import Dispatchers
from .groups import ProcessGroupManager
from .types import HasDispatchers


##


class HttpServer(HasDispatchers):
    class Address(ta.NamedTuple):
        a: SocketAddress

    class Handler(ta.NamedTuple):
        h: SimpleHttpHandler

    def __init__(
            self,
            handler: Handler,
            addr: Address,  # = Address(('localhost', 8000)),
            *,
            exit_stack: contextlib.ExitStack,
    ) -> None:
        super().__init__()

        self._handler = handler.h
        self._addr = addr.a

        self._server = ServerSocketFdioHandler(self._addr, self._on_connect)

        self._conns: ta.List[CoroHttpServerConnectionFdioHandler] = []

        exit_stack.callback(self._server.close)

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
        conn = CoroHttpServerConnectionFdioHandler(
            sock,
            addr,
            self._handler,
        )

        self._conns.append(conn)


##


class SupervisorSimpleHttpHandler(SimpleHttpHandler_):
    def __init__(
            self,
            *,
            groups: ProcessGroupManager,
    ) -> None:
        super().__init__()

        self._groups = groups

    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
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

        return SimpleHttpHandlerResponse(
            200,
            data=json.dumps(dct, **JSON_PRETTY_KWARGS).encode('utf-8') + b'\n',
            headers={
                'Content-Type': 'application/json',
            },
        )
