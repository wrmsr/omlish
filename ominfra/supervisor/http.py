# ruff: noqa: UP006 UP007 UP045
import contextlib
import logging
import socket
import typing as ta

from omlish.http.simple.handlers import ExceptionLoggingSimpleHttpHandler
from omlish.http.simple.handlers import LoggingSimpleHttpHandler
from omlish.http.simple.pipelines.handlers import SimpleHttpHandlerServerIoPipelineHandler
from omlish.http.simple.responses import SimpleHttpHandlerResponses
from omlish.http.simple.types import SimpleHttpHandler
from omlish.http.simple.types import SimpleHttpHandler_
from omlish.http.simple.types import SimpleHttpHandlerRequest
from omlish.http.simple.types import SimpleHttpHandlerResponse
from omlish.http.simple.urlrouting import UrlRoutingSimpleHttpHandler
from omlish.http.urlrouting.router import UrlRouter
from omlish.http.urlrouting.types import UrlRoute
from omlish.http.urlrouting.types import UrlRouteMatch
from omlish.io.fdio.handlers import ServerSocketFdioHandler
from omlish.io.pipelines.drivers.fdio import IoPipelineDriverSocketFdioHandler
from omlish.lite.check import check
from omlish.lite.marshal import marshal_obj
from omlish.logs.modules import get_module_logger
from omlish.sockets.addresses import SocketAddress

from .dispatchers import Dispatchers
from .group import ProcessGroup
from .group import ProcessGroupManager
from .process import PidMap
from .process import Process
from .types import HasDispatchers
from .utils.ostypes import Pid


log = get_module_logger(globals())


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

            if conn.is_active:
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
            pid_map: PidMap,
    ) -> None:
        super().__init__()

        self._groups = groups
        self._pid_map = pid_map

        self._router = UrlRouter([
            UrlRoute('/', self._handle_index, methods={'GET'}),
            UrlRoute('/process/{namespec_or_pid}', self._handle_process, methods={'GET'}),
        ])

        handler: SimpleHttpHandler = UrlRoutingSimpleHttpHandler(self._router)

        handler = LoggingSimpleHttpHandler(handler, log, logging.INFO)
        handler = ExceptionLoggingSimpleHttpHandler(handler, log)

        self._handler = handler

    #

    def _process_to_json(
            self,
            process: Process,
            req: ta.Optional[SimpleHttpHandlerRequest] = None,
            *,
            config: ta.Optional[bool] = None,
            internal: ta.Optional[bool] = None,
    ) -> dict:
        if req is not None:
            if config is None and 'config' in req.parsed.qs:
                config = True
            if internal is None and '_internal' in req.parsed.qs:
                internal = True

        return {
            'name': process.name,
            'namespec': process.namespec,
            'pid': process.pid,

            'state': process.state.name,

            **({'config': marshal_obj(process.config)} if config else {}),

            **({'_internal': marshal_obj(getattr(process, '_internal'))} if internal else {}),
        }

    def _group_to_json(
            self,
            group: ProcessGroup,
            req: ta.Optional[SimpleHttpHandlerRequest] = None,
            *,
            config: ta.Optional[bool] = None,
    ) -> dict:
        if req is not None:
            if config is None and 'config' in req.parsed.qs:
                config = True

        return {
            'name': group.name,

            **({'config': marshal_obj(group.config)} if config else {}),
        }

    #

    def _handle_process(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        match = req.context[UrlRouteMatch]

        process: ta.Optional[Process] = None
        namespec_or_pid = match.values['namespec_or_pid']
        try:
            pid = int(namespec_or_pid)
        except ValueError:
            namespec = namespec_or_pid
            gn, pn = namespec.split(':')
            if (group := self._groups.get(gn)) is not None:
                process = group.get(pn)
        else:
            process = self._pid_map.get(Pid(pid))
        if process is None:
            return SimpleHttpHandlerResponses.not_found()

        return SimpleHttpHandlerResponses.json(
            self._process_to_json(process, req),
            style='pretty',
        )

    def _handle_index(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        return SimpleHttpHandlerResponses.json(
            {
                'groups': {
                    g.name: {
                        **self._group_to_json(g, req),
                        'processes': {
                            p.name: self._process_to_json(p, req)
                            for p in g
                        },
                    }
                    for g in self._groups
                },
            },
            style='pretty',
        )

    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        return self._handler(req)
