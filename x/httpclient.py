"""
TODO:
 - !! clean headers lol
 - async
 - stream
"""
import abc
import http.client
import urllib.error
import urllib.request
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang


if ta.TYPE_CHECKING:
    import httpx
else:
    httpx = lang.proxy_import('httpx')


StrOrBytes: ta.TypeAlias = str | bytes
CanHttpHeaders: ta.TypeAlias = ta.Union[
    'HttpHeaders',
    ta.Mapping[StrOrBytes, StrOrBytes | ta.Sequence[StrOrBytes]],
    ta.Sequence[tuple[StrOrBytes, StrOrBytes]],
]


class HttpHeaders:
    def __init__(self, src: CanHttpHeaders) -> None:
        super().__init__()

        if isinstance(src, HttpHeaders):
            check.is_(src, self)
            return

        raise NotImplementedError

    def __new__(cls, obj: CanHttpHeaders) -> 'HttpHeaders':
        if isinstance(obj, HttpHeaders):
            return obj

        return super().__new__(cls)


@dc.dataclass(frozen=True)
class HttpRequest(lang.Final):
    url: str
    method: str = 'GET'

    _: dc.KW_ONLY

    headers: CanHttpHeaders | None = dc.xfield(None, repr=dc.truthy_repr)
    data: bytes | None = dc.xfield(None, repr_fn=lambda v: '...' if v is not None else None)

    timeout: float | None = None

    @cached.property
    def headers_(self) -> HttpHeaders:
        return HttpHeaders(self.headers)


@dc.dataclass(frozen=True)
class HttpResponse(lang.Final):
    req: HttpRequest

    _: dc.KW_ONLY

    headers: HttpHeaders | None = dc.xfield(None, repr=dc.truthy_repr)
    data: bytes | None = dc.xfield(None, repr_fn=lambda v: '...' if v is not None else None)

    underlying: ta.Any = dc.field(default=None, repr=False)


class HttpError(Exception):
    pass


class HttpClient(lang.Abstract):
    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abc.abstractmethod
    def request(self, req: HttpRequest) -> HttpResponse:
        raise NotImplementedError


class UrllibHttpClient(HttpClient):
    def request(self, req: HttpRequest) -> HttpResponse:
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(
                        req.url,
                        method=req.method,
                        headers=req.headers or {},
                        data=req.data,
                    ),
                    timeout=req.timeout,
            ) as resp:
                return HttpResponse(
                    req=req,
                    headers=dict(resp.headers.items()),
                    data=resp.read(),
                    underlying=resp,
                )
        except (urllib.error.URLError, http.client.HTTPException) as e:
            raise HttpError from e


class HttpxHttpClient(HttpClient):
    def request(self, req: HttpRequest) -> HttpResponse:
        try:
            response = httpx.request(
                method=req.method,
                url=req.url,
                headers=req.headers,
                content=req.data,
                timeout=req.timeout,
            )
            return HttpResponse(
                req=req,
                headers=response.headers,
                data=response.content,
                underlying=response,
            )
        except httpx.HTTPError as e:
            raise HttpError from e


def _main() -> None:
    for cls in [
        UrllibHttpClient,
        HttpxHttpClient,
    ]:
        with cls() as cli:
            resp = cli.request(HttpRequest('https://www.google.com'))
            print(resp)


if __name__ == '__main__':
    _main()
