# ruff: noqa: UP043 UP045
# @omlish-lite
import abc
import contextlib
import dataclasses as dc
import typing as ta

from ...io.readers import AsyncBufferedBytesReader
from ...lite.abstract import Abstract
from ...lite.dataclasses import dataclass_shallow_asdict
from .base import BaseHttpClient
from .base import BaseHttpResponse
from .base import BaseHttpResponseT
from .base import HttpClientContext
from .base import HttpRequest
from .base import HttpResponse
from .base import HttpStatusError


AsyncStreamHttpResponseT = ta.TypeVar('AsyncStreamHttpResponseT', bound='AsyncStreamHttpResponse')
AsyncHttpClientT = ta.TypeVar('AsyncHttpClientT', bound='AsyncHttpClient')


##


@ta.final
@dc.dataclass(frozen=True)  # kw_only=True
class AsyncStreamHttpResponse(BaseHttpResponse):
    _stream: ta.Optional[AsyncBufferedBytesReader] = None

    @property
    def stream(self) -> 'AsyncBufferedBytesReader':
        if (st := self._stream) is None:
            raise TypeError('No data')
        return st

    @property
    def has_data(self) -> bool:
        return self._stream is not None

    #

    _closer: ta.Optional[ta.Callable[[], ta.Awaitable[None]]] = None

    async def __aenter__(self: AsyncStreamHttpResponseT) -> AsyncStreamHttpResponseT:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self) -> None:
        if (c := self._closer) is not None:
            await c()  # noqa


#


async def async_close_http_client_response(resp: BaseHttpResponse) -> None:
    if isinstance(resp, HttpResponse):
        pass

    elif isinstance(resp, AsyncStreamHttpResponse):
        await resp.close()

    else:
        raise TypeError(resp)


@contextlib.asynccontextmanager
async def async_closing_http_client_response(resp: BaseHttpResponseT) -> ta.AsyncGenerator[BaseHttpResponseT, None]:
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


async def async_read_http_client_response(resp: BaseHttpResponse) -> HttpResponse:
    if isinstance(resp, HttpResponse):
        return resp

    elif isinstance(resp, AsyncStreamHttpResponse):
        return HttpResponse(**{
            **{k: v for k, v in dataclass_shallow_asdict(resp).items() if k not in ('_stream', '_closer')},
            **({'data': await resp.stream.readall()} if resp.has_data else {}),
        })

    else:
        raise TypeError(resp)


##


class AsyncHttpClient(BaseHttpClient, Abstract):
    async def __aenter__(self: AsyncHttpClientT) -> AsyncHttpClientT:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def request(
            self,
            req: HttpRequest,
            *,
            context: ta.Optional[HttpClientContext] = None,
            check: bool = False,
    ) -> HttpResponse:
        async with async_closing_http_client_response(await self.stream_request(
                req,
                context=context,
                check=check,
        )) as resp:
            return await async_read_http_client_response(resp)

    async def stream_request(
            self,
            req: HttpRequest,
            *,
            context: ta.Optional[HttpClientContext] = None,
            check: bool = False,
    ) -> AsyncStreamHttpResponse:
        if context is None:
            context = HttpClientContext()

        resp = await self._stream_request(context, req)

        try:
            if check and not resp.is_success:
                if isinstance(resp.underlying, Exception):
                    cause = resp.underlying
                else:
                    cause = None
                raise HttpStatusError(await async_read_http_client_response(resp)) from cause  # noqa

        except Exception:
            await async_close_http_client_response(resp)
            raise

        return resp

    @abc.abstractmethod
    def _stream_request(self, ctx: HttpClientContext, req: HttpRequest) -> ta.Awaitable[AsyncStreamHttpResponse]:
        raise NotImplementedError
