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

from ..lite.check import check


SocketAddress = ta.Any


##


@dc.dataclass(frozen=True)
class SocketAddressFamily:
    i: int
    name: str

    def __post_init__(self) -> None:
        check.isinstance(self.i, int)
        check.non_empty_str(self.name)


class _SocketAddressFamilies:
    def __init__(self, *sfs: SocketAddressFamily) -> None:
        super().__init__()

        self._sfs = sfs

        by_i: ta.Dict[int, SocketAddressFamily] = {}
        by_name: ta.Dict[str, SocketAddressFamily] = {}
        for sf in sfs:
            check.not_in(sf.i, by_i)
            check.not_in(sf.name, by_name)
            by_i[sf.i] = sf
            by_name[sf.name] = sf
        self._by_i = by_i
        self._by_name = by_name

    def __iter__(self) -> ta.Iterator[SocketAddressFamily]:
        return iter(self._sfs)

    def __len__(self) -> int:
        return len(self._sfs)

    def __getitem__(self, key: ta.Union[int, str]) -> SocketAddressFamily:
        if isinstance(key, int):
            return self._by_i[key]
        elif isinstance(key, str):
            return self._by_name[key]
        else:
            raise TypeError(key)

    def get(self, key: ta.Union[int, str]) -> ta.Optional[SocketAddressFamily]:
        try:
            return self[key]
        except KeyError:
            return None


#


_SOCKET_ADDRESS_FAMILIES: ta.Sequence[SocketAddressFamily] = [
    SocketAddressFamily(
        i=i,
        name=name,
    )
    for name in dir(socket)
    if name.startswith('AF_')
    for i in [getattr(socket, name)]
    if isinstance(i, int)
]


SOCKET_ADDRESS_FAMILIES = _SocketAddressFamilies(*_SOCKET_ADDRESS_FAMILIES)


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
