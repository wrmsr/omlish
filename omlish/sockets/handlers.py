# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import typing as ta

from .addresses import SocketAddress


SocketHandlerFactory = ta.Callable[[SocketAddress, ta.BinaryIO, ta.BinaryIO], 'SocketHandler']


##


class SocketHandler(abc.ABC):
    def __init__(
            self,
            client_address: SocketAddress,
            rfile: ta.BinaryIO,
            wfile: ta.BinaryIO,
    ) -> None:
        super().__init__()

        self._client_address = client_address
        self._rfile = rfile
        self._wfile = wfile

    @abc.abstractmethod
    def handle(self) -> None:
        raise NotImplementedError
