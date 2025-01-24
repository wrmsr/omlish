# ruff: noqa: UP006 UP007
# @omlish-lite
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


@dc.dataclass(frozen=True)
class HttpHandlerResponseStreamedData:
    iter: ta.Iterable[bytes]
    length: ta.Optional[int] = None


class HttpHandlerError(Exception):
    pass


class UnsupportedMethodHttpHandlerError(Exception):
    pass
