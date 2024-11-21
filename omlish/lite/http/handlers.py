# ruff: noqa: UP006 UP007
import dataclasses as dc
import http.server
import typing as ta

from ..socket import SocketAddress
from .parsing import HttpHeaders


HttpHandler = ta.Callable[['HttpHandlerRequest'], 'HttpHandlerResponse']


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
    data: ta.Optional[bytes] = None
    close_connection: ta.Optional[bool] = None


class HttpHandlerError(Exception):
    pass


class UnsupportedMethodHttpHandlerError(Exception):
    pass
