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

        def read1(self, /, n: int = -1) -> bytes:
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

        async def read1(self, /, n: int = -1) -> bytes:
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
            #  - https://github.com/encode/httpx/discussions/2963
            #   - Exception ignored in: <async_generator object HTTP11ConnectionByteStream.__aiter__ at 0x1325a7540>
            #   - RuntimeError: async generator ignored GeneratorExit
            #  - Traced to:
            #   - HTTP11ConnectionByteStream.aclose -> await self._connection._response_closed()
            #   - AsyncHTTP11Connection._response_closed -> async with self._state_lock
            #   - anyio._backends._asyncio.Lock.acquire -> await AsyncIOBackend.cancel_shielded_checkpoint() -> await sleep(0)  # noqa
            #  - Might have something to do with pycharm/pydevd's nested asyncio, doesn't seem to happen under trio ever
            #    or asyncio outside debugger.
            @es.push_async_callback
            async def close_it() -> None:
                try:
                    # print(f'close_it.begin: {it=}', file=sys.stderr)
                    await it.aclose()  # type: ignore[attr-defined]
                    # print(f'close_it.end: {it=}', file=sys.stderr)
                except BaseException as be:  # noqa
                    # print(f'close_it.__exit__: {it=} {be=}', file=sys.stderr)
                    raise
                finally:
                    # print(f'close_it.finally: {it=}', file=sys.stderr)
                    pass

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
