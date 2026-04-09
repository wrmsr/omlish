# ruff: noqa: UP037 UP045
# @omlish-lite
import abc
import contextlib
import dataclasses as dc
import typing as ta

from ...io.readers import BytesReader
from ...lite.abstract import Abstract
from ...lite.dataclasses import dataclass_shallow_asdict
from .base import BaseHttpClient
from .base import BaseHttpClientResponse
from .base import BaseHttpClientResponseT
from .base import HttpClientContext
from .base import HttpClientRequest
from .base import HttpClientResponse
from .base import StatusHttpClientError


StreamHttpClientResponseT = ta.TypeVar('StreamHttpClientResponseT', bound='StreamHttpClientResponse')
HttpClientT = ta.TypeVar('HttpClientT', bound='HttpClient')


##


@ta.final
@dc.dataclass(frozen=True)  # kw_only=True
class StreamHttpClientResponse(BaseHttpClientResponse):
    _stream: ta.Optional[BytesReader] = None

    @property
    def stream(self) -> 'BytesReader':
        if (st := self._stream) is None:
            raise TypeError('No data')
        return st

    @property
    def has_data(self) -> bool:
        return self._stream is not None

    #

    _closer: ta.Optional[ta.Callable[[], None]] = None

    def __enter__(self: StreamHttpClientResponseT) -> StreamHttpClientResponseT:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        if (c := self._closer) is not None:
            c()  # noqa


#


def close_http_client_response(resp: BaseHttpClientResponse) -> None:
    if isinstance(resp, HttpClientResponse):
        pass

    elif isinstance(resp, StreamHttpClientResponse):
        resp.close()

    else:
        raise TypeError(resp)


@contextlib.contextmanager
def closing_http_client_response(resp: BaseHttpClientResponseT) -> ta.Iterator[BaseHttpClientResponseT]:
    if isinstance(resp, HttpClientResponse):
        yield resp
        return

    elif isinstance(resp, StreamHttpClientResponse):
        with contextlib.closing(resp):
            yield resp

    else:
        raise TypeError(resp)


def read_http_client_response(resp: BaseHttpClientResponse) -> HttpClientResponse:
    if isinstance(resp, HttpClientResponse):
        return resp

    elif isinstance(resp, StreamHttpClientResponse):
        return HttpClientResponse(**{
            **{k: v for k, v in dataclass_shallow_asdict(resp).items() if k not in ('_stream', '_closer')},
            **({'data': resp.stream.read()} if resp.has_data else {}),
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
            req: HttpClientRequest,
            *,
            context: ta.Optional[HttpClientContext] = None,
            check: bool = False,
    ) -> HttpClientResponse:
        with closing_http_client_response(self.stream_request(
                req,
                context=context,
                check=check,
        )) as resp:
            return read_http_client_response(resp)

    def stream_request(
            self,
            req: HttpClientRequest,
            *,
            context: ta.Optional[HttpClientContext] = None,
            check: bool = False,
    ) -> StreamHttpClientResponse:
        if context is None:
            context = HttpClientContext()

        resp = self._stream_request(context, req)

        try:
            if check and not resp.is_success:
                if isinstance(resp.underlying, Exception):
                    cause = resp.underlying
                else:
                    cause = None
                raise StatusHttpClientError(read_http_client_response(resp)) from cause  # noqa

        except Exception:
            close_http_client_response(resp)
            raise

        return resp

    @abc.abstractmethod
    def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> StreamHttpClientResponse:
        raise NotImplementedError
