# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - SocketClientAddress family / tuple pairs
  + codification of https://docs.python.org/3/library/socket.html#socket-families
"""
import dataclasses as dc
import socket
import typing as ta


SocketAddress = ta.Any


##


@dc.dataclass(frozen=True)
class SocketAddressInfoArgs:
    host: ta.Optional[str]
    port: ta.Union[str, int, None]
    family: socket.AddressFamily = socket.AddressFamily.AF_UNSPEC
    type: int = 0
    proto: int = 0
    flags: socket.AddressInfo = socket.AddressInfo(0)


@dc.dataclass(frozen=True)
class SocketAddressInfo:
    family: socket.AddressFamily
    type: int
    proto: int
    canonname: ta.Optional[str]
    sockaddr: SocketAddress


def get_best_socket_family(
        host: ta.Optional[str],
        port: ta.Union[str, int, None],
        family: ta.Union[int, socket.AddressFamily] = socket.AddressFamily.AF_UNSPEC,
) -> ta.Tuple[socket.AddressFamily, SocketAddress]:
    """https://github.com/python/cpython/commit/f289084c83190cc72db4a70c58f007ec62e75247"""

    infos = socket.getaddrinfo(
        host,
        port,
        family,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    ai = SocketAddressInfo(*next(iter(infos)))
    return ai.family, ai.sockaddr
