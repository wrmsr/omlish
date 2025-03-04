# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import logging
import typing as ta

from ..addresses import SocketAndAddress
from ..io import close_socket_immediately
from .handlers import SocketServerHandler
from .handlers import SocketServerHandler_


##


@dc.dataclass(frozen=True)
class SslErrorHandlingSocketServerHandler(SocketServerHandler_):
    handler: SocketServerHandler

    log: ta.Optional[logging.Logger] = None

    #

    _error_cls: ta.ClassVar[ta.Optional[ta.Type[BaseException]]] = None

    @classmethod
    def _get_error_cls(cls) -> ta.Type[BaseException]:
        if (error_cls := cls._error_cls) is None:
            import ssl
            error_cls = cls._error_cls = ssl.SSLError
        return error_cls

    def __call__(self, conn: SocketAndAddress) -> None:
        try:
            self.handler(conn)
        except self._get_error_cls():  # noqa
            if (log := self.log) is not None:
                log.exception('SSL Error in connection %r', conn)
            close_socket_immediately(conn.socket)
