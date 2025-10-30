"""
TODO:
 - standardize following redirects
"""
import contextlib
import functools
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ...io.buffers import ReadableListBuffer
from ..headers import HttpHeaders
from .asyncs import AsyncHttpClient
from .asyncs import AsyncStreamHttpResponse
from .base import HttpClientContext
from .base import HttpClientError
from .base import HttpRequest
from .sync import HttpClient
from .sync import StreamHttpResponse


if ta.TYPE_CHECKING:
    import httpx
else:
    httpx = lang.proxy_import('httpx')


##


class HttpxHttpClient(HttpClient):
    @dc.dataclass(frozen=True)
    class _StreamAdapter:
        it: ta.Iterator[bytes]

        def read1(self, n: int = -1, /) -> bytes:
            try:
                return next(self.it)
            except StopIteration:
                return b''

    def _stream_request(self, ctx: HttpClientContext, req: HttpRequest) -> StreamHttpResponse:
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
                _stream=ReadableListBuffer().new_buffered_reader(self._StreamAdapter(resp.iter_bytes())),
                _closer=resp_close,  # type: ignore
            )

        except httpx.HTTPError as e:
            resp_close()
            raise HttpClientError from e

        except BaseException:
            resp_close()
            raise


##


class HttpxAsyncHttpClient(AsyncHttpClient):
    @dc.dataclass(frozen=True)
    class _StreamAdapter:
        it: ta.AsyncIterator[bytes]

        async def read1(self, n: int = -1, /) -> bytes:
            try:
                return await anext(self.it)
            except StopAsyncIteration:
                return b''

    async def _stream_request(self, ctx: HttpClientContext, req: HttpRequest) -> AsyncStreamHttpResponse:
        es = contextlib.AsyncExitStack()

        try:
            client = await es.enter_async_context(httpx.AsyncClient())

            resp = await es.enter_async_context(client.stream(
                method=req.method_or_default,
                url=req.url,
                headers=req.headers_ or None,  # type: ignore
                content=req.data,
                timeout=req.timeout_s,
            ))

            it = resp.aiter_bytes()

            # FIXME:
            #  this has a tendency to raise `RuntimeError: async generator ignored GeneratorExit` when all of the
            #  following conditions are met:
            #   - stopped iterating midway through
            #   - shutting down the event loop
            #   - debugging under pycharm / pydevd
            #   - running under asyncio
            #  it does not seem to happen unless all of these conditions are met. see:
            #   https://gist.github.com/wrmsr/a0578ee5d5371b53804cfb56aeb84cdf .
            es.push_async_callback(it.aclose)  # type: ignore[attr-defined]

            return AsyncStreamHttpResponse(
                status=resp.status_code,
                headers=HttpHeaders(resp.headers.raw),
                request=req,
                underlying=resp,
                _stream=ReadableListBuffer().new_async_buffered_reader(self._StreamAdapter(it)),
                _closer=es.aclose,
            )

        except httpx.HTTPError as e:
            await es.aclose()
            raise HttpClientError from e

        except BaseException:
            await es.aclose()
            raise
