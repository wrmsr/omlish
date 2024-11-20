"""
TODO:
 - SocketClientAddress family / tuple pairs
  + codification of https://docs.python.org/3/library/socket.html#socket-families
"""
import abc
import dataclasses as dc
import socket
import typing as ta


SocketAddress: ta.TypeAlias = ta.Any


##


@dc.dataclass(frozen=True)
class SocketAddressInfoArgs:
    host: str | None
    port: str | int | None
    family: socket.AddressFamily = socket.AddressFamily.AF_UNSPEC
    type: int = 0
    proto: int = 0
    flags: socket.AddressInfo = socket.AddressInfo(0)


@dc.dataclass(frozen=True)
class SocketAddressInfo:
    family: socket.AddressFamily
    type: int
    proto: int
    canonname: str | None
    sockaddr: SocketAddress


def get_best_socket_family(
        host: str | None,
        port: str | int | None,
        family: int | socket.AddressFamily = socket.AddressFamily.AF_UNSPEC,
) -> tuple[socket.AddressFamily, SocketAddress]:
    infos = socket.getaddrinfo(
        host,
        port,
        family,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    ai = SocketAddressInfo(*next(iter(infos)))
    return ai.family, ai.sockaddr


##


SocketRequestHandlerFactory: ta.TypeAlias = ta.Callable[[SocketAddress, ta.IO, ta.IO], 'SocketRequestHandler']


class SocketRequestHandler(abc.ABC):
    def __init__(
            self,
            client_address: SocketAddress,
            rfile: ta.IO,
            wfile: ta.IO,
    ) -> None:
        super().__init__()

        self.client_address = client_address
        self.rfile = rfile
        self.wfile = wfile

    @abc.abstractmethod
    def handle(self) -> None:
        raise NotImplementedError
