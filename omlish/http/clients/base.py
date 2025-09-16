# ruff: noqa: UP006 UP007 UP045
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

from ... import dataclasses as dc
from ...lite.abstract import Abstract
from ...lite.cached import cached_property
from ..headers import CanHttpHeaders
from ..headers import HttpHeaders


BaseHttpResponseT = ta.TypeVar('BaseHttpResponseT', bound='BaseHttpResponse')


##


DEFAULT_ENCODING = 'utf-8'


def is_success_status(status: int) -> bool:
    return 200 <= status < 300


##


@ta.final
@dc.dataclass(frozen=True)
class HttpRequest:
    url: str
    method: ta.Optional[str] = None  # noqa

    _: dc.KW_ONLY

    headers: ta.Optional[CanHttpHeaders] = dc.xfield(None, repr=dc.truthy_repr)
    data: ta.Union[bytes, str, None] = dc.xfield(None, repr_fn=lambda v: '...' if v is not None else None)

    timeout_s: ta.Optional[float] = None

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


@dc.dataclass(frozen=True, kw_only=True)
class BaseHttpResponse(Abstract):
    status: int

    headers: ta.Optional[HttpHeaders] = dc.xfield(None, repr=dc.truthy_repr)

    request: HttpRequest
    underlying: ta.Any = dc.field(default=None, repr=False)

    @property
    def is_success(self) -> bool:
        return is_success_status(self.status)


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class HttpResponse(BaseHttpResponse):
    data: ta.Optional[bytes] = dc.xfield(None, repr_fn=lambda v: '...' if v is not None else None)


##


class HttpClientError(Exception):
    @property
    def cause(self) -> ta.Optional[BaseException]:
        return self.__cause__


@dc.dataclass(frozen=True)
class HttpStatusError(HttpClientError):
    response: HttpResponse
