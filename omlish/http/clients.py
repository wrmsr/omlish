"""
TODO:
 - stream
  - chunk size - httpx interface is awful, punch through?
 - httpx catch
 - return non-200 HttpResponses
 - async
"""
import abc
import contextlib
import functools
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


@dc.dataclass(frozen=True, kw_only=True)
class StreamHttpResponse(BaseHttpResponse, lang.Final):
    class Stream(ta.Protocol):
        def read(self, /, n: int = -1) -> bytes: ...

    stream: Stream

    _closer: ta.Callable[[], None] | None = dc.field(default=None, repr=False)

    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        if (c := self._closer) is not None:
            c()


def close_response(resp: BaseHttpResponse) -> None:
    if isinstance(resp, HttpResponse):
        pass

    elif isinstance(resp, StreamHttpResponse):
        resp.close()

    else:
        raise TypeError(resp)


@contextlib.contextmanager
def closing_response(resp: BaseHttpResponseT) -> ta.Iterator[BaseHttpResponseT]:
    if isinstance(resp, HttpResponse):
        yield resp  # type: ignore
        return

    elif isinstance(resp, StreamHttpResponse):
        with contextlib.closing(resp):
            yield resp  # type: ignore

    else:
        raise TypeError(resp)


def read_response(resp: BaseHttpResponse) -> HttpResponse:
    if isinstance(resp, HttpResponse):
        return resp

    elif isinstance(resp, StreamHttpResponse):
        data = resp.stream.read()
        return HttpResponse(**{
            **{k: v for k, v in dc.shallow_asdict(resp).items() if k not in ('stream', '_closer')},
            'data': data,
        })

    else:
        raise TypeError(resp)


#


class HttpClientError(Exception):
    @property
    def cause(self) -> BaseException | None:
        return self.__cause__


@dc.dataclass(frozen=True)
class HttpStatusError(HttpClientError):
    response: HttpResponse


#


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
        with closing_response(self.stream_request(
            req,
            check=check,
        )) as resp:
            return read_response(resp)

    def stream_request(
            self,
            req: HttpRequest,
            *,
            check: bool = False,
    ) -> StreamHttpResponse:
        resp = self._stream_request(req)

        try:
            if check and not resp.is_success:
                if isinstance(resp.underlying, Exception):
                    cause = resp.underlying
                else:
                    cause = None
                raise HttpStatusError(read_response(resp)) from cause  # noqa

        except Exception:
            close_response(resp)
            raise

        return resp

    @abc.abstractmethod
    def _stream_request(self, req: HttpRequest) -> StreamHttpResponse:
        raise NotImplementedError


##


class UrllibHttpClient(HttpClient):
    def _build_request(self, req: HttpRequest) -> urllib.request.Request:
        d: ta.Any
        if (d := req.data) is not None:
            if isinstance(d, str):
                d = d.encode(DEFAULT_ENCODING)

        # urllib headers are dumb dicts [1], and keys *must* be strings or it will automatically add problematic default
        # headers because it doesn't see string keys in its header dict [2]. frustratingly it has no problem accepting
        # bytes values though [3].
        # [1]: https://github.com/python/cpython/blob/232b303e4ca47892f544294bf42e31dc34f0ec72/Lib/urllib/request.py#L319-L325  # noqa
        # [2]: https://github.com/python/cpython/blob/232b303e4ca47892f544294bf42e31dc34f0ec72/Lib/urllib/request.py#L1276-L1279  # noqa
        # [3]: https://github.com/python/cpython/blob/232b303e4ca47892f544294bf42e31dc34f0ec72/Lib/http/client.py#L1300-L1301  # noqa
        h: dict[str, str] = {}
        if hs := req.headers_:
            for k, v in hs.strict_dct.items():
                h[k.decode('ascii')] = v.decode('ascii')

        return urllib.request.Request(  # noqa
            req.url,
            method=req.method_or_default,
            headers=h,
            data=d,
        )

    def _stream_request(self, req: HttpRequest) -> StreamHttpResponse:
        try:
            resp = urllib.request.urlopen(  # noqa
                self._build_request(req),
                timeout=req.timeout_s,
            )

        except urllib.error.HTTPError as e:
            try:
                return StreamHttpResponse(
                    status=e.code,
                    headers=HttpHeaders(e.headers.items()),
                    request=req,
                    underlying=e,
                    stream=e,
                    _closer=e.close,
                )

            except Exception:
                e.close()
                raise

        except (urllib.error.URLError, http.client.HTTPException) as e:
            raise HttpClientError from e

        try:
            return StreamHttpResponse(
                status=resp.status,
                headers=HttpHeaders(resp.headers.items()),
                request=req,
                underlying=resp,
                stream=resp,
                _closer=resp.close,
            )

        except Exception:  # noqa
            resp.close()
            raise


##


class HttpxHttpClient(HttpClient):
    @dc.dataclass(frozen=True)
    class _StreamAdapter:
        it: ta.Iterator[bytes]

        def read(self, /, n: int = -1) -> bytes:
            if n < 0:
                return b''.join(self.it)
            else:
                try:
                    return next(self.it)
                except StopIteration:
                    return b''

    def _stream_request(self, req: HttpRequest) -> StreamHttpResponse:
        try:
            resp_cm = httpx.stream(
                method=req.method_or_default,
                url=req.url,
                headers=req.headers_ or None,  # type: ignore
                content=req.data,
                timeout=req.timeout_s,
            )

        except httpx.HTTPError as e:
            raise HttpClientError from e

        resp_close = functools.partial(resp_cm.__exit__, None, None, None)

        try:
            resp = resp_cm.__enter__()
            return StreamHttpResponse(
                status=resp.status_code,
                headers=HttpHeaders(resp.headers.raw),
                request=req,
                underlying=resp,
                stream=self._StreamAdapter(resp.iter_bytes()),
                _closer=resp_close,  # type: ignore
            )

        except httpx.HTTPError as e:
            resp_close()
            raise HttpClientError from e

        except Exception:
            resp_close()
            raise


##


def _default_client() -> HttpClient:
    return UrllibHttpClient()


def client() -> HttpClient:
    return _default_client()


def request(
        url: str,
        method: str | None = None,
        *,
        headers: CanHttpHeaders | None = None,
        data: bytes | str | None = None,

        timeout_s: float | None = None,

        check: bool = False,

        client: HttpClient | None = None,  # noqa

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

    def do(cli: HttpClient) -> HttpResponse:
        return cli.request(
            req,

            check=check,
        )

    if client is not None:
        return do(client)

    else:
        with _default_client() as cli:
            return do(cli)
