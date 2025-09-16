# ruff: noqa: UP043 UP045
# @omlish-lite
import abc
import contextlib
import dataclasses as dc
import typing as ta

from ...lite.abstract import Abstract
from ...lite.dataclasses import dataclass_maybe_post_init
from ...lite.dataclasses import dataclass_shallow_asdict
from .base import BaseHttpResponse
from .base import BaseHttpResponseT
from .base import HttpRequest
from .base import HttpResponse
from .base import HttpStatusError


AsyncStreamHttpResponseT = ta.TypeVar('AsyncStreamHttpResponseT', bound='AsyncStreamHttpResponse')
AsyncHttpClientT = ta.TypeVar('AsyncHttpClientT', bound='AsyncHttpClient')


##


@ta.final
@dc.dataclass(frozen=True)  # kw_only=True
class AsyncStreamHttpResponse(BaseHttpResponse):
    class Stream(ta.Protocol):
        def read(self, /, n: int = -1) -> ta.Awaitable[bytes]: ...

    @ta.final
    class _NullStream:
        def read(self, /, n: int = -1) -> ta.Awaitable[bytes]:
            raise TypeError

    stream: Stream = _NullStream()

    _closer: ta.Optional[ta.Callable[[], ta.Awaitable[None]]] = None

    def __post_init__(self) -> None:
        dataclass_maybe_post_init(super())
        if isinstance(self.stream, AsyncStreamHttpResponse._NullStream):
            raise TypeError(self.stream)

    async def __aenter__(self: AsyncStreamHttpResponseT) -> AsyncStreamHttpResponseT:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self) -> None:
        if (c := self._closer) is not None:
            c()


#


async def async_close_response(resp: BaseHttpResponse) -> None:
    if isinstance(resp, HttpResponse):
        pass

    elif isinstance(resp, AsyncStreamHttpResponse):
        await resp.close()

    else:
        raise TypeError(resp)


@contextlib.asynccontextmanager
async def async_closing_response(resp: BaseHttpResponseT) -> ta.AsyncGenerator[BaseHttpResponseT, None]:
    if isinstance(resp, HttpResponse):
        yield resp
        return

    elif isinstance(resp, AsyncStreamHttpResponse):
        try:
            yield resp
        finally:
            await resp.close()

    else:
        raise TypeError(resp)


async def async_read_response(resp: BaseHttpResponse) -> HttpResponse:
    if isinstance(resp, HttpResponse):
        return resp

    elif isinstance(resp, AsyncStreamHttpResponse):
        data = await resp.stream.read()
        return HttpResponse(**{
            **{k: v for k, v in dataclass_shallow_asdict(resp).items() if k not in ('stream', '_closer')},
            'data': data,
        })

    else:
        raise TypeError(resp)


##


class AsyncHttpClient(Abstract):
    async def __aenter__(self: AsyncHttpClientT) -> AsyncHttpClientT:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def request(
            self,
            req: HttpRequest,
            *,
            check: bool = False,
    ) -> HttpResponse:
        async with async_closing_response(await self.stream_request(
                req,
                check=check,
        )) as resp:
            return await async_read_response(resp)

    async def stream_request(
            self,
            req: HttpRequest,
            *,
            check: bool = False,
    ) -> AsyncStreamHttpResponse:
        resp = await self._stream_request(req)

        try:
            if check and not resp.is_success:
                if isinstance(resp.underlying, Exception):
                    cause = resp.underlying
                else:
                    cause = None
                raise HttpStatusError(await async_read_response(resp)) from cause  # noqa

        except Exception:
            await async_close_response(resp)
            raise

        return resp

    @abc.abstractmethod
    def _stream_request(self, req: HttpRequest) -> ta.Awaitable[AsyncStreamHttpResponse]:
        raise NotImplementedError
