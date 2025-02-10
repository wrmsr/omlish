# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import typing as ta

from .addresses import SocketAddress
from .io import SocketIoPair  # noqa


SocketHandler = ta.Callable[[SocketAddress, 'SocketIoPair'], None]  # ta.TypeAlias


##


class SocketHandler_(abc.ABC):  # noqa
    @abc.abstractmethod
    def __call__(self, addr: SocketAddress, f: SocketIoPair) -> None:
        raise NotImplementedError


class SocketHandlerClose(Exception):  # noqa
    pass
