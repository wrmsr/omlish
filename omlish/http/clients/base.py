# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - ?? lite ?? whole point is an async client in lite code
 - stream
  - chunk size - httpx interface is awful, punch through?
 - httpx catch
 - return non-200 HttpResponses
 - async
"""
import dataclasses as dc
import typing as ta

from ...lite.abstract import Abstract
from ...lite.attrops import AttrOps
from ...lite.cached import cached_property
from ..headers import CanHttpHeaders
from ..headers import HttpHeaders


BaseHttpClientResponseT = ta.TypeVar('BaseHttpClientResponseT', bound='BaseHttpClientResponse')


##


DEFAULT_HTTP_CLIENT_ENCODING = 'utf-8'


def is_success_http_status(status: int) -> bool:
    return 200 <= status < 300


##


@ta.final
@dc.dataclass(frozen=True)
class HttpClientRequest:
    url: str
    method: ta.Optional[str] = None  # noqa

    # _: dc.KW_ONLY

    headers: ta.Optional[CanHttpHeaders] = None
    data: ta.Union[bytes, str, None] = None

    timeout_s: ta.Optional[float] = None

    #

    __repr__ = AttrOps['HttpClientRequest'](lambda o: (
        o.url,
        o.method,
        (o.headers, dict(repr_fn=AttrOps.truthy_repr)),
        (o.data, dict(repr_fn=lambda v: '...' if v is not None else None)),
        (o.timeout_s, dict(repr_fn=AttrOps.opt_repr)),
    )).repr

    #

    @property
    def method_or_default(self) -> str:
        if self.method is not None:
            return self.method
        if self.data is not None:
            return 'POST'
        return 'GET'

    @cached_property
    def headers_(self) -> ta.Optional[HttpHeaders]:
        return HttpHeaders(self.headers) if self.headers is not None else None


#


@dc.dataclass(frozen=True)  # kw_only=True
class BaseHttpClientResponse(Abstract):
    request: HttpClientRequest

    status: int

    headers: ta.Optional[HttpHeaders] = None

    underlying: ta.Any = None

    #

    __repr__ = AttrOps['BaseHttpClientResponse'](lambda o: (
        o.status,
        (o.headers, dict(repr_fn=AttrOps.truthy_repr)),
        o.request,
    )).repr

    #

    @property
    def is_success(self) -> bool:
        return is_success_http_status(self.status)


@ta.final
@dc.dataclass(frozen=True)  # kw_only=True
class HttpClientResponse(BaseHttpClientResponse):
    data: ta.Optional[bytes] = None

    #

    __repr__ = AttrOps['HttpClientResponse'](lambda o: (
        o.status,
        (o.headers, dict(repr_fn=AttrOps.truthy_repr)),
        (o.data, dict(repr_fn=lambda v: '...' if v is not None else None)),
        o.request,
    )).repr


##


@ta.final
class HttpClientContext:
    def __init__(self) -> None:
        self._dct: dict = {}


##


class HttpClientError(Exception):
    @property
    def cause(self) -> ta.Optional[BaseException]:
        return self.__cause__


@dc.dataclass()
class StatusHttpClientError(HttpClientError):
    response: HttpClientResponse


##


class BaseHttpClient(Abstract):
    pass
