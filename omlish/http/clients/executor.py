# ruff: noqa: UP043 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from .asyncs import AsyncHttpClient
from .asyncs import AsyncStreamHttpClientResponse
from .base import HttpClientContext
from .base import HttpClientRequest
from .sync import HttpClient
from .sync import StreamHttpClientResponse


##


class ExecutorAsyncHttpClient(AsyncHttpClient):
    def __init__(
            self,
            run_in_executor: ta.Callable[..., ta.Awaitable],
            client: HttpClient,
    ) -> None:
        super().__init__()

        self._run_in_executor = run_in_executor
        self._client = client

    @dc.dataclass(frozen=True)
    class _StreamAdapter:
        owner: 'ExecutorAsyncHttpClient'
        resp: StreamHttpClientResponse

        async def read1(self, n: int = -1, /) -> bytes:
            return await self.owner._run_in_executor(self.resp.stream.read1, n)  # noqa

        async def read(self, n: int = -1, /) -> bytes:
            return await self.owner._run_in_executor(self.resp.stream.read, n)  # noqa

        async def close(self) -> None:
            return await self.owner._run_in_executor(self.resp.close)  # noqa

    async def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> AsyncStreamHttpClientResponse:
        resp: StreamHttpClientResponse = await self._run_in_executor(lambda: self._client.stream_request(req, context=ctx))  # noqa
        return AsyncStreamHttpClientResponse(
            status=resp.status,
            headers=resp.headers,
            request=req,
            underlying=resp,
            **(dict(  # type: ignore
                _stream=(adapter := self._StreamAdapter(self, resp)),
                _closer=adapter.close,
            ) if resp.has_data else {}),
        )
