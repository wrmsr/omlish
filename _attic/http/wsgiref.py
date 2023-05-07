import logging
import socket as sock
import threading
import typing as ta
import wsgiref.simple_server

from .. import lang
from .apps import App
from .bind import Binder
from .bind import ClientAddress
from .servers import WsgiServer
from .types import Environ


log = logging.getLogger(__name__)


WsgiRequestHandler = wsgiref.simple_server.WSGIRequestHandler


class WsgiRefProtocol(lang.Protocol):

    @property
    def server_name(self) -> str:
        raise NotImplementedError

    @property
    def server_port(self) -> int:
        raise NotImplementedError

    @property
    def base_environ(self) -> Environ:
        raise NotImplementedError

    def get_app(self) -> App:
        raise NotImplementedError

    def handle_error(self, request: sock.socket, client_address: ClientAddress) -> None:
        raise NotImplementedError


@lang.protocol_check(WsgiRefProtocol)
class WsgiRefWsgiServer(WsgiServer):

    Handler = ta.Callable[[sock.socket, ClientAddress, 'WsgiRefWsgiServer'], None]

    def __init__(
            self,
            binder: Binder,
            app: App,
            *,
            handler: Handler = WsgiRequestHandler,
            **kwargs
    ) -> None:
        super().__init__(binder, app, **kwargs)

        self._handler = handler

    @property
    def server_name(self) -> str:
        return self.binder.name

    @property
    def server_port(self) -> int:
        return self.binder.port

    def get_app(self) -> App:
        return self._app

    def handle_request(self, request: sock.socket, client_address: ClientAddress) -> None:
        self._handler(request, client_address, self)


class SerialWsgiRefServer(WsgiRefWsgiServer):
    pass


class ThreadSpawningWsgiRefServer(WsgiRefWsgiServer):

    def process_request(self, request: sock.socket, client_address: ClientAddress) -> None:
        thread = threading.Thread(target=super().process_request, args=(request, client_address))
        thread.start()
