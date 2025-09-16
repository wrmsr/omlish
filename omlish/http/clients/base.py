"""
TODO:
 - ?? lite ?? whole point is an async client in lite code
 - stream
  - chunk size - httpx interface is awful, punch through?
 - httpx catch
 - return non-200 HttpResponses
 - async
"""
import typing as ta

from ... import cached
from ... import dataclasses as dc
from ... import lang
from ..headers import CanHttpHeaders
from ..headers import HttpHeaders


BaseHttpResponseT = ta.TypeVar('BaseHttpResponseT', bound='BaseHttpResponse')


##


DEFAULT_ENCODING = 'utf-8'


def is_success_status(status: int) -> bool:
    return 200 <= status < 300


##


@dc.dataclass(frozen=True)
class HttpRequest(lang.Final):
    url: str
    method: str | None = None  # noqa

    _: dc.KW_ONLY

    headers: CanHttpHeaders | None = dc.xfield(None, repr=dc.truthy_repr)
    data: bytes | str | None = dc.xfield(None, repr_fn=lambda v: '...' if v is not None else None)

    timeout_s: float | None = None

    #

    @property
    def method_or_default(self) -> str:
        if self.method is not None:
            return self.method
        if self.data is not None:
            return 'POST'
        return 'GET'

    @cached.property
    def headers_(self) -> HttpHeaders | None:
        return HttpHeaders(self.headers) if self.headers is not None else None


#


@dc.dataclass(frozen=True, kw_only=True)
class BaseHttpResponse(lang.Abstract):
    status: int

    headers: HttpHeaders | None = dc.xfield(None, repr=dc.truthy_repr)

    request: HttpRequest
    underlying: ta.Any = dc.field(default=None, repr=False)

    @property
    def is_success(self) -> bool:
        return is_success_status(self.status)


@dc.dataclass(frozen=True, kw_only=True)
class HttpResponse(BaseHttpResponse, lang.Final):
    data: bytes | None = dc.xfield(None, repr_fn=lambda v: '...' if v is not None else None)


##


class HttpClientError(Exception):
    @property
    def cause(self) -> BaseException | None:
        return self.__cause__


@dc.dataclass(frozen=True)
class HttpStatusError(HttpClientError):
    response: HttpResponse
