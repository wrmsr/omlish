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
        buf: ReadableListBuffer = dc.field(default_factory=ReadableListBuffer)

        def read1(self, /, n: int = -1) -> bytes:
            if n < 0:
                if (b := self.buf.read(n)) is not None:
                    return b
                try:
                    return next(self.it)
                except StopIteration:
                    return b''

            else:
                while len(self.buf) < n:
                    try:
                        b = next(self.it)
                    except StopIteration:
                        b = b''
                    if not b:
                        return self.buf.read() or b''
                    self.buf.feed(b)
                return self.buf.read(n) or b''

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


class HttpxAsyncHttpClient(AsyncHttpClient):
    @dc.dataclass(frozen=True)
    class _StreamAdapter:
        it: ta.AsyncIterator[bytes]
        buf: ReadableListBuffer = dc.field(default_factory=ReadableListBuffer)

        async def read1(self, /, n: int = -1) -> bytes:
            if n < 0:
                if (b := self.buf.read(n)) is not None:
                    return b
                try:
                    return await anext(self.it)
                except StopAsyncIteration:
                    return b''

            else:
                while len(self.buf) < n:
                    try:
                        b = await anext(self.it)
                    except StopAsyncIteration:
                        b = b''
                    if not b:
                        return self.buf.read() or b''
                    self.buf.feed(b)
                return self.buf.read(n) or b''

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

            return AsyncStreamHttpResponse(
                status=resp.status_code,
                headers=HttpHeaders(resp.headers.raw),
                request=req,
                underlying=resp,
                stream=self._StreamAdapter(resp.aiter_bytes()),
                _closer=es.aclose,
            )

        except httpx.HTTPError as e:
            await es.aclose()
            raise HttpClientError from e

        except Exception:
            await es.aclose()
            raise
