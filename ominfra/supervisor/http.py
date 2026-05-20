# ruff: noqa: UP006 UP007 UP045
import contextlib
import json
import socket
import typing as ta

from omlish.http.simple.pipelines.handlers import SimpleHttpHandlerServerIoPipelineHandler
from omlish.http.simple.types import SimpleHttpHandler
from omlish.http.simple.types import SimpleHttpHandler_
from omlish.http.simple.types import SimpleHttpHandlerRequest
from omlish.http.simple.types import SimpleHttpHandlerResponse
from omlish.io.fdio.handlers import ServerSocketFdioHandler
from omlish.io.pipelines.drivers.fdio import IoPipelineDriverSocketFdioHandler
from omlish.lite.check import check
from omlish.lite.json import JSON_PRETTY_KWARGS
from omlish.lite.marshal import marshal_obj
from omlish.sockets.addresses import SocketAddress

from .dispatchers import Dispatchers
from .group import ProcessGroupManager
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

        self._conns: ta.List[IoPipelineDriverSocketFdioHandler] = []

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
        try:
            conn = IoPipelineDriverSocketFdioHandler(
                sock,
                addr,
                SimpleHttpHandlerServerIoPipelineHandler.build_standard_pipeline_spec(
                    sock,
                    addr,
                    self._handler,
                ),
            )

            check.none(conn.next())

            if conn.is_running:
                self._conns.append(conn)

            else:
                conn.close()

        except BaseException:  # noqa
            sock.close()

            raise


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
            'groups': {
                g.name: {
                    'processes': {
                        p.name: {
                            'pid': p.pid,
                            'state': p.state.name,
                            **({'_internal': marshal_obj(getattr(p, '_internal'))} if req.path == '/_internal' else {}),
                        }
                        for p in g
                    },
                }
                for g in self._groups
            },
        }

        return SimpleHttpHandlerResponse(
            status=200,
            data=json.dumps(dct, **JSON_PRETTY_KWARGS).encode('utf-8') + b'\n',
            headers={
                'Content-Type': 'application/json',
            },
        )
