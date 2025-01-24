# ruff: noqa: UP006 UP007
# @omlish-lite
import typing as ta

from .addresses import SocketAddress
from .io import SocketIoPair  # noqa


SocketHandler = ta.Callable[[SocketAddress, 'SocketIoPair'], 'SocketHandler']  # ta.TypeAlias


##
