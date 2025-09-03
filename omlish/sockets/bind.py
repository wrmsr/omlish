# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - def parse: (<bind>)?:<port>, unix://, fd://
 - unix chown/chgrp
 - DupSocketBinder
 - udp
"""
import abc
import dataclasses as dc
import errno
import os
import socket as socket_
import stat
import typing as ta

from ..lite.abstract import Abstract
from ..lite.check import check
from ..lite.dataclasses import dataclass_maybe_post_init
from .addresses import SocketAddress
from .addresses import SocketAndAddress


SocketBinderT = ta.TypeVar('SocketBinderT', bound='SocketBinder')
SocketBinderConfigT = ta.TypeVar('SocketBinderConfigT', bound='SocketBinder.Config')

CanSocketBinderConfig = ta.Union['SocketBinder.Config', int, ta.Tuple[str, int], str]  # ta.TypeAlias
CanSocketBinder = ta.Union['SocketBinder', CanSocketBinderConfig]  # ta.TypeAlias


##


class SocketBinder(Abstract, ta.Generic[SocketBinderConfigT]):
    @dc.dataclass(frozen=True)
    class Config:
        listen_backlog: int = 5

        allow_reuse_address: bool = True
        allow_reuse_port: bool = True

        set_inheritable: bool = False

        #

        @classmethod
        def of(cls, obj: CanSocketBinderConfig) -> 'SocketBinder.Config':
            if isinstance(obj, SocketBinder.Config):
                return obj

            elif isinstance(obj, int):
                return TcpSocketBinder.Config(
                    port=obj,
                )

            elif isinstance(obj, tuple):
                host, port = obj
                return TcpSocketBinder.Config(
                    host=host,
                    port=port,
                )

            elif isinstance(obj, str):
                return UnixSocketBinder.Config(
                    file=obj,
                )

            else:
                raise TypeError(obj)

    #

    def __init__(self, config: SocketBinderConfigT) -> None:
        super().__init__()

        self._config = config

    #

    @classmethod
    def of(cls, obj: CanSocketBinder) -> 'SocketBinder':
        if isinstance(obj, SocketBinder):
            return obj

        config: SocketBinder.Config
        if isinstance(obj, SocketBinder.Config):
            config = obj

        else:
            config = SocketBinder.Config.of(obj)

        if isinstance(config, TcpSocketBinder.Config):
            return TcpSocketBinder(config)

        elif isinstance(config, UnixSocketBinder.Config):
            return UnixSocketBinder(config)

        else:
            raise TypeError(config)

    #

    class Error(RuntimeError):
        pass

    class NotBoundError(Error):
        pass

    class AlreadyBoundError(Error):
        pass

    #

    @property
    @abc.abstractmethod
    def address_family(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def address(self) -> SocketAddress:
        raise NotImplementedError

    #

    _socket: socket_.socket

    @property
    def is_bound(self) -> bool:
        return hasattr(self, '_socket')

    @property
    def socket(self) -> socket_.socket:
        try:
            return self._socket
        except AttributeError:
            raise self.NotBoundError from None

    _name: str

    @property
    def name(self) -> str:
        try:
            return self._name
        except AttributeError:
            raise self.NotBoundError from None

    _port: ta.Optional[int]

    @property
    def port(self) -> ta.Optional[int]:
        try:
            return self._port
        except AttributeError:
            raise self.NotBoundError from None

    #

    def fileno(self) -> int:
        return self.socket.fileno()

    #

    def __enter__(self: SocketBinderT) -> SocketBinderT:
        self.bind()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    #

    def _init_socket(self) -> None:
        if hasattr(self, '_socket'):
            raise self.AlreadyBoundError

        sock = socket_.socket(self.address_family, socket_.SOCK_STREAM)
        self._socket = sock

        if self._config.allow_reuse_address and hasattr(socket_, 'SO_REUSEADDR'):
            sock.setsockopt(socket_.SOL_SOCKET, socket_.SO_REUSEADDR, 1)

        # Since Linux 6.12.9, SO_REUSEPORT is not allowed on other address families than AF_INET/AF_INET6.
        if (
                self._config.allow_reuse_port and hasattr(socket_, 'SO_REUSEPORT') and
                self.address_family in (socket_.AF_INET, socket_.AF_INET6)
        ):
            try:
                sock.setsockopt(socket_.SOL_SOCKET, socket_.SO_REUSEPORT, 1)
            except OSError as err:
                if err.errno not in (errno.ENOPROTOOPT, errno.EINVAL):
                    raise

        if self._config.set_inheritable and hasattr(sock, 'set_inheritable'):
            sock.set_inheritable(True)

    def _pre_bind(self) -> None:
        pass

    def _post_bind(self) -> None:
        pass

    def bind(self) -> None:
        self._init_socket()

        self._pre_bind()

        self.socket.bind(self.address)

        self._post_bind()

        check.state(all(hasattr(self, a) for a in ('_socket', '_name', '_port')))

    #

    def close(self) -> None:
        if hasattr(self, '_socket'):
            self._socket.close()

    #

    def listen(self) -> None:
        self.socket.listen(self._config.listen_backlog)

    @abc.abstractmethod
    def accept(self, sock: ta.Optional[socket_.socket] = None) -> SocketAndAddress:
        raise NotImplementedError


##


class TcpSocketBinder(SocketBinder):
    @dc.dataclass(frozen=True)
    class Config(SocketBinder.Config):
        DEFAULT_HOST: ta.ClassVar[str] = 'localhost'
        host: str = DEFAULT_HOST

        port: int = 0

        def __post_init__(self) -> None:
            dataclass_maybe_post_init(super())
            check.non_empty_str(self.host)
            check.isinstance(self.port, int)
            check.arg(self.port > 0)

    def __init__(self, config: Config) -> None:
        super().__init__(check.isinstance(config, self.Config))

        self._address = (config.host, config.port)

    #

    address_family = socket_.AF_INET

    @property
    def address(self) -> SocketAddress:
        return self._address

    #

    def _post_bind(self) -> None:
        super()._post_bind()

        host, port, *_ = self.socket.getsockname()

        self._name = socket_.getfqdn(host)
        self._port = port

    #

    def accept(self, sock: ta.Optional[socket_.socket] = None) -> SocketAndAddress:
        if sock is None:
            sock = self.socket

        conn, client_address = sock.accept()
        return SocketAndAddress(conn, client_address)


##


class UnixSocketBinder(SocketBinder):
    @dc.dataclass(frozen=True)
    class Config(SocketBinder.Config):
        file: str = ''

        unlink: bool = False

        def __post_init__(self) -> None:
            dataclass_maybe_post_init(super())
            check.non_empty_str(self.file)

    def __init__(self, config: Config) -> None:
        super().__init__(check.isinstance(config, self.Config))

        self._address = config.file

    #

    address_family = socket_.AF_UNIX

    @property
    def address(self) -> SocketAddress:
        return self._address

    #

    def _pre_bind(self) -> None:
        super()._pre_bind()

        if self._config.unlink:
            try:
                if stat.S_ISSOCK(os.stat(self._config.file).st_mode):
                    os.unlink(self._config.file)
            except FileNotFoundError:
                pass

    def _post_bind(self) -> None:
        super()._post_bind()

        name = self.socket.getsockname()

        os.chmod(name, stat.S_IRWXU | stat.S_IRWXG)  # noqa

        self._name = name
        self._port = None

    #

    def accept(self, sock: ta.Optional[socket_.socket] = None) -> SocketAndAddress:
        if sock is None:
            sock = self.socket

        conn, _ = sock.accept()
        client_address = ('', 0)
        return SocketAndAddress(conn, client_address)
