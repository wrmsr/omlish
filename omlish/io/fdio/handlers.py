# ruff: noqa: UP006 UP007 UP045
import abc
import socket
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
            addr: SocketAddress,
            sock: socket.socket,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._sock: ta.Optional[socket.socket] = sock

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
        cli_sock, cli_addr = check.not_none(self._sock).accept()
        cli_sock.setblocking(False)

        self._on_connect(cli_sock, cli_addr)
