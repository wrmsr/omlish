# ruff: noqa: UP043 UP045
# @omlish-lite
import typing as ta

from ...lite.abstract import Abstract
from .asyncs import AsyncHttpClient
from .asyncs import AsyncStreamHttpResponse
from .base import BaseHttpResponse
from .base import HttpClientContext
from .base import HttpRequest
from .sync import HttpClient
from .sync import StreamHttpResponse


SyncOrAsyncHttpClientT = ta.TypeVar('SyncOrAsyncHttpClientT', bound=ta.Union['HttpClient', 'AsyncHttpClient'])


##


class HttpClientMiddleware(Abstract):
    def process_request(self, ctx: HttpClientContext, req: HttpRequest) -> HttpRequest:
        return req

    def process_response(self, ctx: HttpClientContext, resp: BaseHttpResponse) -> ta.Union[BaseHttpResponse, HttpRequest]:  # noqa
        return resp


class AbstractMiddlewareHttpClient(Abstract, ta.Generic[SyncOrAsyncHttpClientT]):
    def __init__(
            self,
            client: SyncOrAsyncHttpClientT,
            middlewares: ta.Iterable[HttpClientMiddleware],
    ) -> None:
        super().__init__()

        self._client = client
        self._middlewares = list(middlewares)

    def _process_request(self, ctx: HttpClientContext, req: HttpRequest) -> HttpRequest:
        for mw in self._middlewares:
            req = mw.process_request(ctx, req)
        return req


class MiddlewareHttpClient(AbstractMiddlewareHttpClient[HttpClient], HttpClient):
    def _stream_request(self, ctx: HttpClientContext, req: HttpRequest) -> StreamHttpResponse:
        return self._client.stream_request(self._process_request(ctx, req))


class MiddlewareAsyncHttpClient(AbstractMiddlewareHttpClient[AsyncHttpClient], AsyncHttpClient):
    def _stream_request(self, ctx: HttpClientContext, req: HttpRequest) -> ta.Awaitable[AsyncStreamHttpResponse]:
        return self._client.stream_request(self._process_request(ctx, req))


##


class RedirectHandlingHttpClientMiddleware(HttpClientMiddleware):
    def process_request(self, ctx: HttpClientContext, req: HttpRequest) -> HttpRequest:
        raise NotImplementedError
