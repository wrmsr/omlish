import abc
import collections.abc
import contextlib
import json
import logging
import os
import selectors
import socket as sock
import stat
import sys
import threading
import traceback
import types
import typing as ta
import wsgiref.simple_server

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.http import consts as hc


log = logging.getLogger(__name__)


##


AppT = ta.TypeVar('AppT', bound='App')
Environ = ta.Dict[str, ta.Any]
StartResponse = ta.Callable[[str, ta.List[ta.Tuple[str, str]]], ta.Callable[[lang.BytesLike], None]]
RawApp = ta.Callable[[Environ, StartResponse], ta.Iterable[lang.BytesLike]]
AppLike = ta.Union['App', RawApp]
BadRequestExceptionT = ta.TypeVar('BadRequestExceptionT', bound='BadRequestException')


class BadRequestException(Exception):
    pass


class App(lang.Abstract):

    def __enter__(self: AppT) -> AppT:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return None

    @abc.abstractmethod
    def __call__(self, environ: Environ, start_response: StartResponse) -> ta.Iterable[bytes]:
        raise NotImplementedError


##


BinderT = ta.TypeVar('BinderT', bound='Binder')
ClientAddress = tuple[str, int]


ADDRESS_FAMILY_NAMES = {
    value: name
    for name in dir(sock)
    if name.startswith('AF_')
    for value in [getattr(sock, name)]
    if isinstance(value, int)
}


class Binder(lang.Abstract):

    @dc.dataclass(frozen=True)
    class Config:
        pass

    @property
    @abc.abstractmethod
    def address_family(self) -> int:
        raise NotImplementedError

    _name: ta.Optional[str] = None

    @property
    def name(self) -> str:
        return check.not_none(self._name)

    _port: ta.Optional[int] = None

    @property
    def port(self) -> int:
        return check.not_none(self._port)

    _socket: ta.Optional[sock.socket] = None

    @property
    def socket(self) -> sock.socket:
        if self._socket is None:
            raise TypeError('Not bound')
        return self._socket

    @abc.abstractmethod
    def _init_socket(self) -> None:
        raise NotImplementedError

    def fileno(self) -> int:
        return self.socket.fileno()

    def __enter__(self: BinderT) -> BinderT:
        if self._socket is not None:
            raise TypeError('Already initialized')
        self._init_socket()
        if not isinstance(self._socket, sock.socket):
            raise TypeError('Initialization failure')
        return self  # type: ignore

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._socket is not None:
            self._socket.close()

    listen_backlog = 5

    def listen(self) -> None:
        self.socket.listen(self.listen_backlog)

    @abc.abstractmethod
    def accept(self, socket: ta.Optional[sock.socket] = None) -> tuple[sock.socket, ClientAddress]:
        raise NotImplementedError

    @classmethod
    def new(cls, target: ta.Union[tuple[str, int], str]) -> 'Binder':
        if isinstance(target, str):
            return UnixBinder(UnixBinder.Config(target))

        elif isinstance(target, tuple):
            host, port = target
            if not isinstance(host, str) or not isinstance(port, int):  # type: ignore
                raise TypeError(target)
            return TcpBinder(TcpBinder.Config(host, port))

        elif isinstance(target, Binder):
            return DupBinder(DupBinder.Config(target))

        else:
            raise TypeError(target)


class DupBinder(Binder):

    def __init__(self, target: Binder) -> None:
        super().__init__()

        self._target = target

    @property
    def address_family(self) -> int:
        return self._target.address_family

    @property
    def name(self) -> str:
        return self._target.name

    @property
    def port(self) -> int:
        return self._target.port

    def _init_socket(self) -> None:
        log.info(f'Duplicating {self._target} as {ADDRESS_FAMILY_NAMES[self._target.address_family]}')
        self._socket = sock.fromfd(self._target.fileno(), self.address_family, sock.SOCK_STREAM)

    def accept(self, socket: ta.Optional[sock.socket] = None) -> tuple[sock.socket, ClientAddress]:
        if socket is None:
            socket = self.socket
        return self._target.accept(socket)


class BindBinder(Binder, lang.Abstract):

    _address: ta.Any = None

    allow_reuse_address = True

    def _init_socket(self) -> None:
        self._socket = sock.socket(self.address_family, sock.SOCK_STREAM)

        if self.allow_reuse_address:
            self.socket.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)

        # if hasattr(socket, 'SO_REUSEPORT'):
        #     try:
        #         self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        #     except socket.error as err:
        #         if err.errno not in (errno.ENOPROTOOPT, errno.EINVAL):
        #             raise

        # if hasattr(self.socket, 'set_inheritable'):
        #     self.socket.set_inheritable(True)

        log.info(f'Binding {self._address} as {ADDRESS_FAMILY_NAMES[self.address_family]}')
        self.socket.bind(self._address)
        self._post_bind()

    @abc.abstractmethod
    def _post_bind(self) -> None:
        raise NotImplementedError


class TcpBinder(BindBinder):

    @dc.dataclass(frozen=True)
    class Config(Binder.Config):
        host: str
        port: int

    address_family = sock.AF_INET

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = check.isinstance(config, TcpBinder.Config)
        self._address = (config.host, config.port)

    def _post_bind(self) -> None:
        host, port, *_ = self.socket.getsockname()
        self._name = sock.getfqdn(host)
        self._port = port

    def accept(self, socket: ta.Optional[sock.socket] = None) -> tuple[sock.socket, ClientAddress]:
        if socket is None:
            socket = self.socket
        conn, client_address = socket.accept()
        return conn, client_address


class UnixBinder(BindBinder):

    @dc.dataclass(frozen=True)
    class Config(Binder.Config):
        address: str

    address_family = sock.AF_UNIX

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = check.isinstance(config, UnixBinder.Config)
        self._address = config.address

    def _post_bind(self) -> None:
        name = self.socket.getsockname()
        os.chmod(name, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        self._name = name
        self._port = 0

    def accept(self, socket: ta.Optional[sock.socket] = None) -> tuple[sock.socket, ClientAddress]:
        if socket is None:
            socket = self.socket
        conn, _ = socket.accept()
        client_address = ('', 0)
        return conn, client_address


##


ClientAddress = tuple[str, int]


class SelectorProtocol(ta.Protocol):

    def register(self, *args, **kwargs) -> None: ...

    def select(self, *args, **kwargs) -> bool: ...


class WsgiServer(lang.ContextManaged, lang.Abstract):

    if hasattr(selectors, 'PollSelector'):
        ServerSelector = selectors.PollSelector
    else:
        ServerSelector = selectors.SelectSelector

    @dc.dataclass(frozen=True)
    class Config:
        poll_interval: float = 0.5
        exit_timeout: float = 10.0

    def __init__(
            self,
            binder: Binder,
            app: App,
            *,
            config: Config = Config(),
            **kwargs: ta.Any
    ) -> None:
        super().__init__(**kwargs)

        self._binder = binder
        self._app = app
        self._config = check.isinstance(config, WsgiServer.Config)

        self._lock = threading.RLock()
        self._is_shutdown = threading.Event()
        self._should_shutdown = False

    def _stop(self) -> None:
        acquired = self._lock.acquire(False)
        if not acquired:
            try:
                if not self._is_shutdown.is_set():
                    self.shutdown(True, self._config.exit_timeout)
            finally:
                self._lock.release()

    @property
    def binder(self) -> Binder:
        return self._binder

    @property
    def app(self) -> App:
        return self._app

    @cached.property
    def base_environ(self) -> ta.Mapping[str, ta.Any]:
        return {
            'SERVER_NAME': self.binder.name,
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'SERVER_PORT': str(self.binder.port),
            'REMOTE_HOST': '',
            'CONTENT_LENGTH': '',
            'SCRIPT_NAME': '',
        }

    @contextlib.contextmanager
    def _listen_context(self) -> ta.Generator[SelectorProtocol, None, None]:
        with contextlib.ExitStack() as exit_stack:
            exit_stack.enter_context(self._lock)
            exit_stack.enter_context(self._binder)

            self._binder.listen()

            self._is_shutdown.clear()
            try:
                # XXX: Consider using another file descriptor or connecting to the socket to wake this up instead of
                # polling. Polling reduces our responsiveness to a shutdown request and wastes cpu at all other times.
                with self.ServerSelector() as selector:
                    selector.register(self._binder.fileno(), selectors.EVENT_READ)

                    yield selector

            finally:
                self._is_shutdown.set()

    @contextlib.contextmanager
    def loop_context(self, poll_interval: int = None) -> ta.Generator[bool, None, None]:
        if poll_interval is None:
            poll_interval = self._config.poll_interval

        with self._listen_context() as selector:
            def loop():
                while not self._should_shutdown:
                    ready = selector.select(poll_interval)

                    if ready:
                        try:
                            request, client_address = self._binder.accept()

                        except OSError:
                            self.handle_error(None, None)
                            return

                        try:
                            self.process_request(request, client_address)

                        except Exception:
                            self.handle_error(request, client_address)
                            self.shutdown_request(request)

                    yield bool(ready)

            yield loop()

    def run(self, poll_interval: int = None) -> None:
        with self.loop_context(poll_interval=poll_interval) as loop:
            for _ in loop:
                pass

    def handle_error(
            self,
            request: ta.Optional[sock.socket],
            client_address: ta.Optional[ClientAddress],
    ) -> None:
        log.exception(f'Server error request={request!r} client_address={client_address!r}')

    def process_request(self, request: sock.socket, client_address: ClientAddress) -> None:
        try:
            self.handle_request(request, client_address)
            self.shutdown_request(request)

        except Exception as e:  # noqa
            self.handle_error(request, client_address)
            self.shutdown_request(request)

    @abc.abstractmethod
    def handle_request(self, request: sock.socket, client_address: ClientAddress) -> None:
        raise NotImplementedError

    def shutdown_request(self, request: sock.socket) -> None:
        try:
            # explicitly shutdown. socket.close() merely releases the socket and waits for GC to perform the actual
            # close.
            request.shutdown(sock.SHUT_WR)

        except OSError:
            # some platforms may raise ENOTCONN here
            pass

        request.close()

    def shutdown(self, block=False, timeout=None):
        self._should_shutdown = True
        if block:
            self._is_shutdown.wait(timeout=timeout)


##


WsgiRequestHandler = wsgiref.simple_server.WSGIRequestHandler


class WsgiRefProtocol(ta.Protocol):

    @property
    def server_name(self) -> str: ...

    @property
    def server_port(self) -> int: ...

    @property
    def base_environ(self) -> Environ: ...

    def get_app(self) -> App: ...

    def handle_error(self, request: sock.socket, client_address: ClientAddress) -> None: ...


class WsgiRefWsgiServer(WsgiServer):

    Handler = ta.Callable[[sock.socket, ClientAddress, 'WsgiRefWsgiServer'], None]

    def __init__(
            self,
            binder: Binder,
            app: App,
            *,
            handler: Handler = WsgiRequestHandler,
            **kwargs: ta.Any
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


##


def read_input(environ: Environ) -> bytes:
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    return environ['wsgi.input'].read(request_body_size)


class SimpleDictApp(App):

    class _BadRequestHandledException(Exception):
        pass

    Target = ta.Callable[[ta.Optional[ta.Dict[str, ta.Any]]], ta.Dict[str, ta.Any]]

    def __init__(
            self,
            target: Target,
            encode: ta.Callable[[ta.Any], ta.Any],
            decode: ta.Callable[[ta.Any], ta.Any],
            content_type: str,
            *,
            stream: bool = False,
            stream_separator: bytes = b'\n',
            stream_terminator: bytes = b'\0',
            handle_bad_requests: bool = False,
            on_bad_request: ta.Callable[[ta.Type[BadRequestExceptionT], BadRequestExceptionT, types.TracebackType], None] = None,  # noqa
            **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self._target = check.callable(target)
        self._encode = check.callable(encode)
        self._decode = check.callable(decode)
        self._content_type = check.isinstance(content_type, str)

        self._stream = stream
        self._stream_separator = stream_separator
        self._stream_terminator = stream_terminator

        self._handle_bad_requests = handle_bad_requests
        self._on_bad_request = on_bad_request

    def __call__(self, environ: Environ, start_response: StartResponse) -> ta.Iterable[bytes]:
        request_body = read_input(environ)

        if request_body:
            input = self._decode(request_body)
        else:
            input = None

        @contextlib.contextmanager
        def bad_request_manager():
            if not self._handle_bad_requests:
                yield
                return

            try:
                yield
            except BadRequestException:
                exc_info = sys.exc_info()
                if self._on_bad_request is not None:
                    self._on_bad_request(*exc_info)
                write = start_response(
                    hc.STATUS_BAD_REQUEST.decode(),
                    [hc.CONTENT_TYPE_TEXT.decode()],
                    exc_info=exc_info,
                )
                write('\n'.join(traceback.TracebackException(*exc_info).format()).encode('utf-8'))
                raise self._BadRequestHandledException

        try:
            with bad_request_manager():
                output = self._target(input)
        except self._BadRequestHandledException:
            return []

        start_response(
            hc.STATUS_OK,
            [(hc.HEADER_CONTENT_TYPE.decode(), self._content_type)],
        )

        if output is None:
            return []

        elif isinstance(output, collections.abc.Iterator):
            if not self._stream:
                raise TypeError(output)

            def inner():
                try:
                    with bad_request_manager():
                        for item in output:
                            yield self._encode(item)
                            yield self._stream_separator
                        yield self._stream_terminator
                except self._BadRequestHandledException:
                    pass

            return inner()

        else:
            return [self._encode(output)]


def simple_json_app(target: SimpleDictApp.Target) -> App:
    return SimpleDictApp(
        target,
        lambda output: json.dumps(output).encode('utf-8'),
        lambda request_body: json.loads(request_body.decode('utf-8')),
        hc.CONTENT_TYPE_JSON.decode(),
    )


##
import time

import requests

from omlish.testing import run_with_timeout


def test_inline_http():
    server: ta.Optional[WsgiServer] = None

    def app(environ, start_response):
        assert environ['PATH_INFO'] == '/test'
        start_response(hc.STATUS_OK, [])
        server.shutdown()
        return [b'hi']

    port = 9999

    def fn1():
        time.sleep(0.5)
        while True:
            try:
                response: requests.Response
                with contextlib.closing(requests.post(f'http://localhost:{port}/test', timeout=0.1)) as response:
                    if response.status_code == 200:
                        return
            except requests.RequestException:
                pass
            time.sleep(0.1)

    thread = threading.Thread(target=fn1)
    thread.start()

    with ThreadSpawningWsgiRefServer(TcpBinder(TcpBinder.Config('0.0.0.0', port)), app) as server:
        with server.loop_context() as loop:
            port = server.binder.port
            for _ in loop:
                pass

    thread.join()


def test_http():
    # FIXME: dynamic port
    server: ta.Optional[WsgiServer] = None

    def app(environ, start_response):
        assert environ['PATH_INFO'] == '/test'
        start_response(hc.STATUS_OK, [])
        server.shutdown()
        return [b'hi']

    port = 8181

    def fn0():
        nonlocal server
        server = ThreadSpawningWsgiRefServer(TcpBinder(TcpBinder.Config('0.0.0.0', port)), app)
        server.run()

    def fn1():
        time.sleep(0.5)
        while True:
            try:
                response: requests.Response
                with contextlib.closing(requests.post(f'http://localhost:{port}/test', timeout=0.1)) as response:
                    if response.status_code == 200:
                        return
            except requests.RequestException:
                pass
            time.sleep(0.1)

    run_with_timeout(fn0, fn1)


def test_json_http():
    server: ta.Optional[WsgiServer] = None

    def json_app(obj):
        server.shutdown()
        return {'hi': True}

    port = 9998

    def fn1():
        time.sleep(0.5)
        while True:
            try:
                response: requests.Response
                with contextlib.closing(requests.post(f'http://localhost:{port}/test', timeout=0.1)) as response:
                    if response.status_code == 200:
                        assert json.loads(response.content) == {'hi': True}
                        return
            except requests.RequestException:
                pass
            time.sleep(0.1)

    thread = threading.Thread(target=fn1)
    thread.start()

    with ThreadSpawningWsgiRefServer(
            TcpBinder(TcpBinder.Config('0.0.0.0', 0)),
            simple_json_app(json_app)
    ) as server:
        with server.loop_context() as loop:
            port = server.binder.port
            for _ in loop:
                pass

    thread.join()


##


def _main() -> None:
    def app(environ, start_response):
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']

        if (cl := environ.get('CONTENT_LENGTH')):
            data = environ['wsgi.input'].read(int(cl))
        else:
            data = b''

        start_response(hc.STATUS_OK, [])
        return ['\n'.join([
            f'method: {method}',
            f'path: {path}',
            f'data: {len(data)}',
            '',
        ]).encode()]

    port = 8000

    server = ThreadSpawningWsgiRefServer(
        TcpBinder(TcpBinder.Config('0.0.0.0', port)),
        app,
    )
    server.run()


if __name__ == '__main__':
    _main()
