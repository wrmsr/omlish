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
