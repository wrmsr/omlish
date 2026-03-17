# ruff: noqa: UP043 UP045
# @omlish-lite
import dataclasses as dc

from .asyncs import AsyncHttpClient
from .asyncs import AsyncStreamHttpClientResponse
from .base import HttpClientContext
from .base import HttpClientRequest
from .sync import HttpClient
from .sync import StreamHttpClientResponse


##


class SyncAsyncHttpClient(AsyncHttpClient):
    def __init__(self, client: HttpClient) -> None:
        super().__init__()

        self._client = client

    @dc.dataclass(frozen=True)
    class _StreamAdapter:
        ul: StreamHttpClientResponse

        async def read1(self, n: int = -1, /) -> bytes:
            return self.ul.stream.read1(n)

        async def read(self, n: int = -1, /) -> bytes:
            return self.ul.stream.read(n)

        async def readall(self) -> bytes:
            return self.ul.stream.readall()

        async def close(self) -> None:
            self.ul.close()

    async def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> AsyncStreamHttpClientResponse:
        resp = self._client.stream_request(req, context=ctx)
        return AsyncStreamHttpClientResponse(
            status=resp.status,
            headers=resp.headers,
            request=req,
            underlying=resp,
            **(dict(  # type: ignore
                _stream=(adapter := self._StreamAdapter(resp)),
                _closer=adapter.close,
            ) if resp.has_data else {}),
        )
