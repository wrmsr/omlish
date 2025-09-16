import abc
import contextlib
import typing as ta

from ... import dataclasses as dc
from ... import lang
from .base import BaseHttpResponse
from .base import BaseHttpResponseT
from .base import HttpRequest
from .base import HttpResponse
from .base import HttpStatusError


##


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


#


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
        yield resp
        return

    elif isinstance(resp, StreamHttpResponse):
        with contextlib.closing(resp):
            yield resp

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


##


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
