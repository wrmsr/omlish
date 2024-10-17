"""
TODO:
 - check=False
 - return non-200 HttpResponses
 - async
 - stream
"""
import abc
import http.client
import typing as ta
import urllib.error
import urllib.request

from .. import cached
from .. import dataclasses as dc
from .. import lang
from .headers import CanHttpHeaders
from .headers import HttpHeaders


if ta.TYPE_CHECKING:
    import httpx
else:
    httpx = lang.proxy_import('httpx')


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


@dc.dataclass(frozen=True, kw_only=True)
class HttpResponse(lang.Final):
    status: int

    headers: HttpHeaders | None = dc.xfield(None, repr=dc.truthy_repr)
    data: bytes | None = dc.xfield(None, repr_fn=lambda v: '...' if v is not None else None)

    request: HttpRequest
    underlying: ta.Any = dc.field(default=None, repr=False)

    #

    @property
    def is_success(self) -> bool:
        return is_success_status(self.status)


class HttpClientError(Exception):
    @property
    def cause(self) -> BaseException | None:
        return self.__cause__


@dc.dataclass(frozen=True)
class HttpStatusError(HttpClientError):
    response: HttpResponse


class HttpClient(lang.Abstract):
    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def request(
            self,
            req: HttpRequest,
            *,
            check: bool = False,
    ) -> HttpResponse:
        resp = self._request(req)

        if check and not resp.is_success:
            if isinstance(resp.underlying, Exception):
                cause = resp.underlying
            else:
                cause = None
            raise HttpStatusError(resp) from cause

        return resp

    @abc.abstractmethod
    def _request(self, req: HttpRequest) -> HttpResponse:
        raise NotImplementedError


##


class UrllibHttpClient(HttpClient):
    def _request(self, req: HttpRequest) -> HttpResponse:
        d: ta.Any
        if (d := req.data) is not None:
            if isinstance(d, str):
                d = d.encode(DEFAULT_ENCODING)

        try:
            with urllib.request.urlopen(  # noqa
                    urllib.request.Request(  # noqa
                        req.url,
                        method=req.method_or_default,
                        headers=req.headers_ or {},  # type: ignore
                        data=d,
                    ),
                    timeout=req.timeout_s,
            ) as resp:
                return HttpResponse(
                    status=resp.status,
                    headers=HttpHeaders(resp.headers.items()),
                    data=resp.read(),
                    request=req,
                    underlying=resp,
                )

        except urllib.error.HTTPError as e:
            return HttpResponse(
                status=e.code,
                headers=HttpHeaders(e.headers.items()),
                data=e.read(),
                request=req,
                underlying=e,
            )

        except (urllib.error.URLError, http.client.HTTPException) as e:
            raise HttpClientError from e


##


class HttpxHttpClient(HttpClient):
    def _request(self, req: HttpRequest) -> HttpResponse:
        try:
            response = httpx.request(
                method=req.method_or_default,
                url=req.url,
                headers=req.headers_ or None,  # type: ignore
                content=req.data,
                timeout=req.timeout_s,
            )

            return HttpResponse(
                status=response.status_code,
                headers=HttpHeaders(response.headers.raw),
                data=response.content,
                request=req,
                underlying=response,
            )

        except httpx.HTTPError as e:
            raise HttpClientError from e


##


def client() -> HttpClient:
    return UrllibHttpClient()


def request(
        url: str,
        method: str | None = None,
        *,
        headers: CanHttpHeaders | None = None,
        data: bytes | str | None = None,

        timeout_s: float | None = None,

        check: bool = False,

        **kwargs: ta.Any,
) -> HttpResponse:
    req = HttpRequest(
        url,
        method=method,

        headers=headers,
        data=data,

        timeout_s=timeout_s,

        **kwargs,
    )

    with client() as cli:
        return cli.request(
            req,

            check=check,
        )