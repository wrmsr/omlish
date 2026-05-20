# ruff: noqa: UP006 UP007 UP045
import contextlib
import socket
import typing as ta

from omlish.http.simple.pipelines.handlers import SimpleHttpHandlerServerIoPipelineHandler
from omlish.http.simple.responses import SimpleHttpHandlerResponses
from omlish.http.simple.types import SimpleHttpHandler
from omlish.http.simple.types import SimpleHttpHandler_
from omlish.http.simple.types import SimpleHttpHandlerRequest
from omlish.http.simple.types import SimpleHttpHandlerResponse
from omlish.http.simple.urlrouting import UrlRoutingSimpleHttpHandler
from omlish.http.urlrouting.router import UrlRouter
from omlish.http.urlrouting.types import UrlRoute
from omlish.io.fdio.handlers import ServerSocketFdioHandler
from omlish.io.pipelines.drivers.fdio import IoPipelineDriverSocketFdioHandler
from omlish.lite.check import check
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

        self._router = UrlRouter([
            UrlRoute('/', self._handle_index),
            UrlRoute('/_internal', self._handle_index),
        ])

        self._router_handler = UrlRoutingSimpleHttpHandler(self._router)

    def _handle_index(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
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

        return SimpleHttpHandlerResponses.of_json(
            dct,
            style='pretty',
        )

    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        return self._router_handler(req)
