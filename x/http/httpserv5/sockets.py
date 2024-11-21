"""
TODO:
 - SocketClientAddress family / tuple pairs
  + codification of https://docs.python.org/3/library/socket.html#socket-families
"""
import abc
import typing as ta

from omlish.lite.sockets import SocketAddress


##


SocketHandlerFactory: ta.TypeAlias = ta.Callable[[SocketAddress, ta.BinaryIO, ta.BinaryIO], 'SocketHandler']  # noqa


class SocketHandler(abc.ABC):
    def __init__(
            self,
            client_address: SocketAddress,
            rfile: ta.BinaryIO,
            wfile: ta.BinaryIO,
    ) -> None:
        super().__init__()

        self.client_address = client_address
        self.rfile = rfile
        self.wfile = wfile

    @abc.abstractmethod
    def handle(self) -> None:
        raise NotImplementedError
