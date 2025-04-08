import functools
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..headers import HttpHeaders
from .base import HttpClient
from .base import HttpClientError
from .base import HttpRequest
from .base import StreamHttpResponse


if ta.TYPE_CHECKING:
    import httpx
else:
    httpx = lang.proxy_import('httpx')


##


class HttpxHttpClient(HttpClient):
    @dc.dataclass(frozen=True)
    class _StreamAdapter:
        it: ta.Iterator[bytes]

        def read(self, /, n: int = -1) -> bytes:
            if n < 0:
                return b''.join(self.it)
            else:
                try:
                    return next(self.it)
                except StopIteration:
                    return b''

    def _stream_request(self, req: HttpRequest) -> StreamHttpResponse:
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
