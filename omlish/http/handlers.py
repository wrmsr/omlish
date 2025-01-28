# ruff: noqa: UP006 UP007
# @omlish-lite
import abc
import dataclasses as dc
import http.server
import typing as ta

from ..sockets.addresses import SocketAddress
from .parsing import HttpHeaders


HttpHandler = ta.Callable[['HttpHandlerRequest'], 'HttpHandlerResponse']  # ta.TypeAlias
HttpHandlerResponseData = ta.Union[bytes, 'HttpHandlerResponseStreamedData']  # ta.TypeAlias  # noqa


##


@dc.dataclass(frozen=True)
class HttpHandlerRequest:
    client_address: SocketAddress
    method: str
    path: str
    headers: HttpHeaders
    data: ta.Optional[bytes]


@dc.dataclass(frozen=True)
class HttpHandlerResponse:
    status: ta.Union[http.HTTPStatus, int]

    headers: ta.Optional[ta.Mapping[str, str]] = None
    data: ta.Optional[HttpHandlerResponseData] = None
    close_connection: ta.Optional[bool] = None

    def close(self) -> None:
        if isinstance(d := self.data, HttpHandlerResponseStreamedData):
            d.close()


@dc.dataclass(frozen=True)
class HttpHandlerResponseStreamedData:
    iter: ta.Iterable[bytes]
    length: ta.Optional[int] = None

    def close(self) -> None:
        if hasattr(d := self.iter, 'close'):
            d.close()  # noqa


class HttpHandlerError(Exception):
    pass


class UnsupportedMethodHttpHandlerError(Exception):
    pass


class HttpHandler_(abc.ABC):  # noqa
    @abc.abstractmethod
    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        raise NotImplementedError
