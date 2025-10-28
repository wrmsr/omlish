# ruff: noqa: UP007 UP043 UP045
# @omlish-lite
"""
TODO:
 - redirect
  - referrer header?
  - non-forwarded headers, host check, etc lol
 - 'check' kw becomes StatusCheckingMiddleware?
"""
import dataclasses as dc
import typing as ta
import urllib.parse

from ...lite.abstract import Abstract
from ...lite.check import check
from ..urls import parsed_url_replace
from .asyncs import AsyncHttpClient
from .asyncs import AsyncStreamHttpResponse
from .base import BaseHttpClient
from .base import BaseHttpResponse
from .base import HttpClientContext
from .base import HttpClientError
from .base import HttpRequest
from .sync import HttpClient
from .sync import StreamHttpResponse
from .sync import close_http_client_response


BaseHttpClientT = ta.TypeVar('BaseHttpClientT', bound=BaseHttpClient)


##


class HttpClientMiddleware(Abstract):
    def process_request(
            self,
            ctx: HttpClientContext,
            req: HttpRequest,
    ) -> HttpRequest:
        return req

    def process_response(
            self,
            ctx: HttpClientContext,
            req: HttpRequest,
            resp: BaseHttpResponse,
    ) -> ta.Union[BaseHttpResponse, HttpRequest]:
        return resp


class AbstractMiddlewareHttpClient(Abstract, ta.Generic[BaseHttpClientT]):
    def __init__(
            self,
            client: BaseHttpClientT,
            middlewares: ta.Iterable[HttpClientMiddleware],
    ) -> None:
        super().__init__()

        self._client = client
        self._middlewares = list(middlewares)

    def _process_request(
            self,
            ctx: HttpClientContext,
            req: HttpRequest,
    ) -> HttpRequest:
        for mw in self._middlewares:
            req = mw.process_request(ctx, req)
        return req

    def _process_response(
            self,
            ctx: HttpClientContext,
            req: HttpRequest,
            resp: BaseHttpResponse,
    ) -> ta.Union[BaseHttpResponse, HttpRequest]:
        for mw in self._middlewares:
            nxt = mw.process_response(ctx, req, resp)
            if isinstance(nxt, HttpRequest):
                return nxt
            else:
                resp = nxt
        return resp


#


class MiddlewareHttpClient(AbstractMiddlewareHttpClient[HttpClient], HttpClient):
    def _stream_request(self, ctx: HttpClientContext, req: HttpRequest) -> StreamHttpResponse:
        while True:
            req = self._process_request(ctx, req)

            resp = self._client.stream_request(req, context=ctx)

            try:
                out = self._process_response(ctx, req, resp)

                if isinstance(out, HttpRequest):
                    close_http_client_response(resp)
                    req = out
                    continue

                elif isinstance(out, StreamHttpResponse):
                    return out

                else:
                    raise TypeError(out)  # noqa

            except Exception:
                close_http_client_response(resp)
                raise

        raise RuntimeError


class MiddlewareAsyncHttpClient(AbstractMiddlewareHttpClient[AsyncHttpClient], AsyncHttpClient):
    def _stream_request(self, ctx: HttpClientContext, req: HttpRequest) -> ta.Awaitable[AsyncStreamHttpResponse]:
        return self._client.stream_request(self._process_request(ctx, req))


##


class TooManyRedirectsHttpClientError(HttpClientError):
    pass


class RedirectHandlingHttpClientMiddleware(HttpClientMiddleware):
    DEFAULT_MAX_REDIRECTS: ta.ClassVar[int] = 5

    def __init__(
            self,
            *,
            max_redirects: ta.Optional[int] = None,
    ) -> None:
        super().__init__()

        if max_redirects is None:
            max_redirects = self.DEFAULT_MAX_REDIRECTS
        self._max_redirects = max_redirects

    @dc.dataclass()
    class _State:
        num_redirects: int = 0

    def _get_state(self, ctx: HttpClientContext) -> _State:
        try:
            return ctx._dct[self._State]  # noqa
        except KeyError:
            ret = ctx._dct[self._State] = self._State()  # noqa
            return ret

    def process_response(
            self,
            ctx: HttpClientContext,
            req: HttpRequest,
            resp: BaseHttpResponse,
    ) -> ta.Union[BaseHttpResponse, HttpRequest]:  # noqa
        if resp.status == 302:
            st = self._get_state(ctx)
            if st.num_redirects >= self._max_redirects:
                raise TooManyRedirectsHttpClientError
            st.num_redirects += 1

            rd_url = check.not_none(resp.headers).single_str_dct['location']

            rd_purl = urllib.parse.urlparse(rd_url)
            if not rd_purl.netloc:
                rq_purl = urllib.parse.urlparse(req.url)
                rd_purl = parsed_url_replace(
                    rd_purl,
                    scheme=rq_purl.scheme,
                    netloc=rq_purl.netloc,
                )
                rd_url = urllib.parse.urlunparse(rd_purl)

            return dc.replace(req, url=rd_url)

        return resp
