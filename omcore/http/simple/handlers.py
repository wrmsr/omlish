# ruff: noqa: UP006 UP007 UP045
# @om-lite
import dataclasses as dc
import logging
import typing as ta

from ...lite.bytes import Bytes
from ...logs.protocols import LoggerLike
from ..statuses import HttpStatus
from .types import SimpleHttpHandler
from .types import SimpleHttpHandler_
from .types import SimpleHttpHandlerRequest
from .types import SimpleHttpHandlerResponse


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
    data: Bytes

    status: ta.Union[HttpStatus, int] = 200
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

    status: ta.Union[HttpStatus, int] = 200
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
