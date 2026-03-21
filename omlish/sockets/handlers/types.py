# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract
from ..addresses import SocketAndAddress


SocketHandler = ta.Callable[['SocketAndAddress'], None]  # ta.TypeAlias


##


class SocketHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, conn: SocketAndAddress) -> None:
        raise NotImplementedError


class SocketHandlerClose(Exception):  # noqa
    pass
