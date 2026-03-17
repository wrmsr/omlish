# ruff: noqa: UP043 UP045
# @omlish-lite
import http.client
import typing as ta
import urllib.error
import urllib.request

from ...io.streams.adapters import ByteStreamBufferBytesReaderAdapter
from ...io.streams.segmented import SegmentedByteStreamBuffer
from ...lite.check import check
from ..headers import HttpHeaders
from .base import DEFAULT_HTTP_CLIENT_ENCODING
from .base import HttpClientContext
from .base import HttpClientError
from .base import HttpClientRequest
from .sync import HttpClient
from .sync import StreamHttpClientResponse


##


class UrllibHttpClient(HttpClient):
    def _build_request(self, req: HttpClientRequest) -> urllib.request.Request:
        d: ta.Any
        if (d := req.data) is not None:
            if isinstance(d, str):
                d = d.encode(DEFAULT_HTTP_CLIENT_ENCODING)

        # urllib headers are dumb dicts [1], and keys *must* be strings or it will automatically add problematic default
        # headers because it doesn't see string keys in its header dict [2]. frustratingly it has no problem accepting
        # bytes values though [3].
        # [1]: https://github.com/python/cpython/blob/232b303e4ca47892f544294bf42e31dc34f0ec72/Lib/urllib/request.py#L319-L325  # noqa
        # [2]: https://github.com/python/cpython/blob/232b303e4ca47892f544294bf42e31dc34f0ec72/Lib/urllib/request.py#L1276-L1279  # noqa
        # [3]: https://github.com/python/cpython/blob/232b303e4ca47892f544294bf42e31dc34f0ec72/Lib/http/client.py#L1300-L1301  # noqa
        h: dict[str, str] = {}
        if hs := req.headers_:
            for k, vs in hs.items():
                h[k] = check.single(vs)

        return urllib.request.Request(  # noqa
            req.url,
            method=req.method_or_default,
            headers=h,
            data=d,
        )

    def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> StreamHttpClientResponse:
        try:
            resp = urllib.request.urlopen(  # noqa
                self._build_request(req),
                timeout=req.timeout_s,
            )

        except urllib.error.HTTPError as e:
            try:
                return StreamHttpClientResponse(
                    status=e.code,
                    headers=HttpHeaders(e.headers.items()),
                    request=req,
                    underlying=e,
                    _closer=e.close,
                )

            except Exception:
                e.close()
                raise

        except (urllib.error.URLError, http.client.HTTPException) as e:
            raise HttpClientError from e

        try:
            # urllib responses do *not* guarantee returning exactly `n` bytes from `.read(n)`, so we need to buffer.
            buf = SegmentedByteStreamBuffer(chunk_size=16 * 1024)

            def fill(n: int, single: bool) -> bool:
                # These are ~mostly~ the same for urllib responses, but called separately nonetheless.
                if single:
                    b = resp.read1(n)
                else:
                    b = resp.read(n)
                if not b:
                    return False
                buf.write(b)
                return True

            return StreamHttpClientResponse(
                status=resp.status,
                headers=HttpHeaders(resp.headers.items()),
                request=req,
                underlying=resp,
                _stream=ByteStreamBufferBytesReaderAdapter(buf, fill=fill),
                _closer=resp.close,
            )

        except Exception:  # noqa
            resp.close()
            raise
