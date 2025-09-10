# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - codification of https://docs.python.org/3/library/socket.html#socket-families
"""
import dataclasses as dc
import socket as socket_
import typing as ta


SocketAddress = ta.Any  # ta.TypeAlias


##


@dc.dataclass(frozen=True)
class SocketAddressInfoArgs:
    host: ta.Optional[str]
    port: ta.Union[str, int, None]
    family: socket_.AddressFamily = socket_.AddressFamily.AF_UNSPEC
    type: int = 0
    proto: int = 0
    flags: socket_.AddressInfo = socket_.AddressInfo(0)


@dc.dataclass(frozen=True)
class SocketAddressInfo:
    family: socket_.AddressFamily
    type: int
    proto: int
    canonname: ta.Optional[str]
    sockaddr: SocketAddress


class SocketFamilyAndAddress(ta.NamedTuple):
    family: socket_.AddressFamily
    address: SocketAddress


def get_best_socket_family(
        host: ta.Optional[str],
        port: ta.Union[str, int, None],
        family: ta.Union[int, socket_.AddressFamily] = socket_.AddressFamily.AF_UNSPEC,
) -> SocketFamilyAndAddress:
    """https://github.com/python/cpython/commit/f289084c83190cc72db4a70c58f007ec62e75247"""

    infos = socket_.getaddrinfo(
        host,
        port,
        family,
        type=socket_.SOCK_STREAM,
        flags=socket_.AI_PASSIVE,
    )
    ai = SocketAddressInfo(*next(iter(infos)))
    return SocketFamilyAndAddress(ai.family, ai.sockaddr)


class SocketAndAddress(ta.NamedTuple):
    socket: socket_.socket
    address: SocketAddress

    def wrap_socket(self, fn: ta.Callable[[socket_.socket], socket_.socket]):
        return self._replace(socket=fn(self.socket))

    @classmethod
    def socket_wrapper(
            cls,
            fn: ta.Callable[[socket_.socket], socket_.socket],
    ) -> ta.Callable[['SocketAndAddress'], 'SocketAndAddress']:
        def inner(conn):
            return conn.wrap_socket(fn)
        return inner
