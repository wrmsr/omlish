# ruff: noqa: UP043
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
class AsyncStreamHttpResponse(BaseHttpResponse, lang.Final):
    class Stream(ta.Protocol):
        def read(self, /, n: int = -1) -> ta.Awaitable[bytes]: ...

    stream: Stream

    _closer: ta.Callable[[], ta.Awaitable[None]] | None = dc.field(default=None, repr=False)

    async def __aenter__(self) -> ta.Self:
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
            **{k: v for k, v in dc.shallow_asdict(resp).items() if k not in ('stream', '_closer')},
            'data': data,
        })

    else:
        raise TypeError(resp)


##


class AsyncHttpClient(lang.Abstract):
    async def __aenter__(self) -> ta.Self:
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
