# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import typing as ta

from ..lite.abstract import Abstract
from .addresses import SocketAddress
from .io import SocketIoPair


SocketHandler = ta.Callable[[SocketAddress, 'SocketIoPair'], None]  # ta.TypeAlias


##


class SocketHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, addr: SocketAddress, f: SocketIoPair) -> None:
        raise NotImplementedError


class SocketHandlerClose(Exception):  # noqa
    pass
