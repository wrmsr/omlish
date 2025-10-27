# ruff: noqa: UP043 UP045
# @omlish-lite
import concurrent.futures as cf
import queue

from .asyncs import AsyncHttpClient
from .asyncs import AsyncStreamHttpResponse
from .base import HttpRequest
from .sync import HttpClient


##


class ExecutorAsyncHttpClient(AsyncHttpClient):
    def __init__(self, executor: cf.Executor, client: HttpClient) -> None:
        super().__init__()

        self._executor = executor
        self._client = client

    async def _stream_request(self, req: HttpRequest) -> AsyncStreamHttpResponse:
        q = queue.Queue()

        def inner():
            with self._client.stream_request(req) as s_resp:
                q.put(s_resp)

        fut = self._executor.submit(inner)  # noqa
        # s_resp = queue.
        raise NotImplementedError
