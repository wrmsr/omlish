# ruff: noqa: UP045
# @omlish-lite
import abc
import contextlib
import dataclasses as dc
import typing as ta

from ...io.readers import BufferedBytesReader
from ...lite.abstract import Abstract
from ...lite.dataclasses import dataclass_shallow_asdict
from .base import BaseHttpClient
from .base import BaseHttpResponse
from .base import BaseHttpResponseT
from .base import HttpClientContext
from .base import HttpRequest
from .base import HttpResponse
from .base import HttpStatusError


StreamHttpResponseT = ta.TypeVar('StreamHttpResponseT', bound='StreamHttpResponse')
HttpClientT = ta.TypeVar('HttpClientT', bound='HttpClient')


##


@ta.final
@dc.dataclass(frozen=True)  # kw_only=True
class StreamHttpResponse(BaseHttpResponse):
    _stream: ta.Optional[BufferedBytesReader] = None

    @property
    def stream(self) -> 'BufferedBytesReader':
        if (st := self._stream) is None:
            raise TypeError('No data')
        return st

    @property
    def has_data(self) -> bool:
        return self._stream is not None

    #

    _closer: ta.Optional[ta.Callable[[], None]] = None

    def __enter__(self: StreamHttpResponseT) -> StreamHttpResponseT:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        if (c := self._closer) is not None:
            c()  # noqa


#


def close_http_client_response(resp: BaseHttpResponse) -> None:
    if isinstance(resp, HttpResponse):
        pass

    elif isinstance(resp, StreamHttpResponse):
        resp.close()

    else:
        raise TypeError(resp)


@contextlib.contextmanager
def closing_http_client_response(resp: BaseHttpResponseT) -> ta.Iterator[BaseHttpResponseT]:
    if isinstance(resp, HttpResponse):
        yield resp
        return

    elif isinstance(resp, StreamHttpResponse):
        with contextlib.closing(resp):
            yield resp

    else:
        raise TypeError(resp)


def read_http_client_response(resp: BaseHttpResponse) -> HttpResponse:
    if isinstance(resp, HttpResponse):
        return resp

    elif isinstance(resp, StreamHttpResponse):
        return HttpResponse(**{
            **{k: v for k, v in dataclass_shallow_asdict(resp).items() if k not in ('_stream', '_closer')},
            **({'data': resp.stream.readall()} if resp.has_data else {}),
        })

    else:
        raise TypeError(resp)


##


class HttpClient(BaseHttpClient, Abstract):
    def __enter__(self: HttpClientT) -> HttpClientT:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def request(
            self,
            req: HttpRequest,
            *,
            context: ta.Optional[HttpClientContext] = None,
            check: bool = False,
    ) -> HttpResponse:
        with closing_http_client_response(self.stream_request(
                req,
                context=context,
                check=check,
        )) as resp:
            return read_http_client_response(resp)

    def stream_request(
            self,
            req: HttpRequest,
            *,
            context: ta.Optional[HttpClientContext] = None,
            check: bool = False,
    ) -> StreamHttpResponse:
        if context is None:
            context = HttpClientContext()

        resp = self._stream_request(context, req)

        try:
            if check and not resp.is_success:
                if isinstance(resp.underlying, Exception):
                    cause = resp.underlying
                else:
                    cause = None
                raise HttpStatusError(read_http_client_response(resp)) from cause  # noqa

        except Exception:
            close_http_client_response(resp)
            raise

        return resp

    @abc.abstractmethod
    def _stream_request(self, ctx: HttpClientContext, req: HttpRequest) -> StreamHttpResponse:
        raise NotImplementedError
