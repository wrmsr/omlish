# ruff: noqa: UP006 UP007 UP045
import abc
import errno
import os
import socket
import stat
import typing as ta

from ...lite.abstract import Abstract
from ...lite.check import check
from ...sockets.addresses import SocketAddress


##


class FdioHandler(Abstract):
    @abc.abstractmethod
    def fd(self) -> int:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def closed(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    #

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return False

    #

    def on_readable(self) -> None:
        raise TypeError

    def on_writable(self) -> None:
        raise TypeError

    def on_error(self, exc: ta.Optional[BaseException] = None) -> None:  # noqa
        pass


##


class SocketFdioHandler(FdioHandler, Abstract):
    def __init__(
            self,
            sock: socket.socket,
            addr: ta.Optional[SocketAddress] = None,
    ) -> None:
        super().__init__()

        self._sock: ta.Optional[socket.socket] = sock
        self._addr = addr

    def fd(self) -> int:
        return check.not_none(self._sock).fileno()

    @property
    def closed(self) -> bool:
        return self._sock is None

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close()
        self._sock = None


#


class ServerSocketFdioHandler(SocketFdioHandler):
    def __init__(
            self,
            sock_or_addr: ta.Union[socket.socket, SocketAddress],
            on_connect: ta.Callable[[socket.socket, SocketAddress], None],
    ) -> None:
        # FIXME: io in ctor
        if isinstance(sock_or_addr, socket.socket):
            sock = sock_or_addr
            addr = sock.getsockname()
        else:
            addr = sock_or_addr
            if isinstance(sock_or_addr, str):
                sock = self._create_unix_socket_server(sock_or_addr)
            else:
                sock = socket.create_server(sock_or_addr)

        sock.setblocking(False)

        super().__init__(sock, addr)

        self._on_connect = on_connect

        sock.listen(1)

    @staticmethod
    def _create_unix_socket_server(path: str) -> socket.socket:
        try:
            return socket.create_server(path, family=socket.AF_UNIX)

        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                try:
                    st = os.stat(path)
                except FileNotFoundError:
                    pass

                else:
                    if stat.S_ISSOCK(st.st_mode):
                        os.unlink(path)
                        return socket.create_server(path, family=socket.AF_UNIX)

            raise

    def readable(self) -> bool:
        return True

    def on_readable(self) -> None:
        cli_sock, cli_addr = check.not_none(self._sock).accept()
        cli_sock.setblocking(False)

        self._on_connect(cli_sock, cli_addr)
