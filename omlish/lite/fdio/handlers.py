# ruff: noqa: UP006 UP007
import abc
import socket
import typing as ta

from ..check import check_not_none
from ..socket import SocketAddress


class FdIoHandler(abc.ABC):
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


class SocketFdIoHandler(FdIoHandler, abc.ABC):
    def __init__(
            self,
            addr: SocketAddress,
            sock: socket.socket,
    ) -> None:
        super().__init__()

        self._addr = addr
        self._sock: ta.Optional[socket.socket] = sock

    def fd(self) -> int:
        return check_not_none(self._sock).fileno()

    @property
    def closed(self) -> bool:
        return self._sock is None

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close()
        self._sock = None
