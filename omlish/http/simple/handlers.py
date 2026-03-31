# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import dataclasses as dc
import http.server
import logging
import typing as ta

from ...lite.abstract import Abstract
from ...logs.protocols import LoggerLike
from ...sockets.addresses import SocketAddress
from ..parsing import ParsedHttpHeaders


SimpleHttpHandler = ta.Callable[['SimpleHttpHandlerRequest'], 'SimpleHttpHandlerResponse']  # ta.TypeAlias
SimpleHttpHandlerResponseData = ta.Union[bytes, 'SimpleHttpHandlerResponseStreamedData']  # ta.TypeAlias  # noqa


##


@dc.dataclass(frozen=True)
class SimpleHttpHandlerRequest:
    client_address: SocketAddress
    method: str
    path: str
    headers: ParsedHttpHeaders
    data: ta.Optional[bytes]


@dc.dataclass(frozen=True)
class SimpleHttpHandlerResponse:
    status: ta.Union[http.HTTPStatus, int]

    headers: ta.Optional[ta.Mapping[str, str]] = None
    data: ta.Optional[SimpleHttpHandlerResponseData] = None
    close_connection: ta.Optional[bool] = None

    def close(self) -> None:
        if isinstance(d := self.data, SimpleHttpHandlerResponseStreamedData):
            d.close()


@dc.dataclass(frozen=True)
class SimpleHttpHandlerResponseStreamedData:
    iter: ta.Iterable[bytes]
    length: ta.Optional[int] = None

    def close(self) -> None:
        if hasattr(d := self.iter, 'close'):
            d.close()  # noqa


class SimpleHttpHandlerError(Exception):
    pass


class UnsupportedMethodSimpleHttpHandlerError(Exception):
    pass


class SimpleHttpHandler_(Abstract):  # noqa
    @abc.abstractmethod
    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class LoggingSimpleHttpHandler(SimpleHttpHandler_):
    handler: SimpleHttpHandler
    log: LoggerLike
    level: int = logging.DEBUG

    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        self.log.log(self.level, '%r', req)
        resp = self.handler(req)
        self.log.log(self.level, '%r', resp)
        return resp


@dc.dataclass(frozen=True)
class ExceptionLoggingSimpleHttpHandler(SimpleHttpHandler_):
    handler: SimpleHttpHandler
    log: LoggerLike
    message: ta.Union[str, ta.Callable[[SimpleHttpHandlerRequest, BaseException], str]] = 'Error in http handler'

    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        try:
            return self.handler(req)
        except Exception as e:  # noqa
            if callable(msg := self.message):
                msg = msg(req, e)
            self.log.exception(msg)
            raise


##


@dc.dataclass(frozen=True)
class BytesResponseSimpleHttpHandler(SimpleHttpHandler_):
    data: bytes

    status: ta.Union[http.HTTPStatus, int] = 200
    content_type: ta.Optional[str] = 'application/octet-stream'
    headers: ta.Optional[ta.Mapping[str, str]] = None
    close_connection: bool = True

    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        return SimpleHttpHandlerResponse(
            status=self.status,
            headers={
                **({'Content-Type': self.content_type} if self.content_type else {}),
                'Content-Length': str(len(self.data)),
                **(self.headers or {}),
            },
            data=self.data,
            close_connection=self.close_connection,
        )


@dc.dataclass(frozen=True)
class StringResponseSimpleHttpHandler(SimpleHttpHandler_):
    data: str

    status: ta.Union[http.HTTPStatus, int] = 200
    content_type: ta.Optional[str] = 'text/plain; charset=utf-8'
    headers: ta.Optional[ta.Mapping[str, str]] = None
    close_connection: bool = True

    def __call__(self, req: SimpleHttpHandlerRequest) -> SimpleHttpHandlerResponse:
        data = self.data.encode('utf-8')
        return SimpleHttpHandlerResponse(
            status=self.status,
            headers={
                **({'Content-Type': self.content_type} if self.content_type else {}),
                'Content-Length': str(len(data)),
                **(self.headers or {}),
            },
            data=data,
            close_connection=self.close_connection,
        )
