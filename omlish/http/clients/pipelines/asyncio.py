# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import asyncio
import dataclasses as dc
import io
import typing as ta

from ....io.pipelines.core import IoPipelineHandlerContext
from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver
from ....io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from ....io.pipelines.handlers.flatmap import FlatMapIoPipelineHandlers
from ....io.streams.types import BytesLike
from ....lite.abstract import Abstract
from ....lite.check import check
from ...clients.asyncs import AsyncHttpClient
from ...clients.asyncs import AsyncStreamHttpClientResponse
from ...clients.base import HttpClientContext
from ...clients.base import HttpClientRequest
from ...pipelines.clients.clients import IoPipelineHttpClientMessages
from ...pipelines.responses import FullIoPipelineHttpResponse
from .base import BaseIoPipelineHttpClient


##


class AsyncioIoPipelineAsyncHttpClient(AsyncHttpClient, BaseIoPipelineHttpClient):
    class _StreamReader(Abstract):
        @abc.abstractmethod
        def read1(self, n: int = -1, /) -> ta.Awaitable[bytes]:
            raise NotImplementedError

        @abc.abstractmethod
        def read(self, n: int = -1, /) -> ta.Awaitable[bytes]:
            raise NotImplementedError

        async def close(self) -> None:
            pass

    class _EmptyStreamReader(_StreamReader):
        async def read1(self, n: int = -1, /) -> bytes:
            return b''

        async def read(self, n: int = -1, /) -> bytes:
            return b''

    class _StaticStreamReader(_StreamReader):
        def __init__(self, b: BytesLike) -> None:
            self._r = io.BytesIO(b)

        async def read1(self, n: int = -1, /) -> bytes:
            return self._r.read1(n)

        async def read(self, n: int = -1, /) -> bytes:
            return self._r.read1(n)

    class _DriverStreamReader(_StreamReader):
        def __init__(
                self,
                drv: SyncSocketIoPipelineDriver,
        ) -> None:
            super().__init__()

            self._drv = drv

            self._done = False

        async def read1(self, n: int = -1, /) -> bytes:
            raise NotImplementedError

        async def read(self, n: int = -1, /) -> bytes:
            raise NotImplementedError

        async def close(self) -> None:
            self._drv.close()

    #

    async def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> AsyncStreamHttpClientResponse:
        prepared = self._prepare_request(req)

        #

        response: ta.Optional[FullIoPipelineHttpResponse] = None

        def on_output(h_ctx: IoPipelineHandlerContext, out: IoPipelineHttpClientMessages.Output) -> None:
            msg = out.msg

            if isinstance(msg, FullIoPipelineHttpResponse):
                nonlocal response
                check.none(response)
                response = msg

                h_ctx.pipeline.feed_in(IoPipelineHttpClientMessages.Close())

            elif isinstance(msg, (IoPipelineMessages.FinalInput, IoPipelineHttpClientMessages.Close)):
                pass

            else:
                raise TypeError(msg)

        pipeline_spec = dc.replace(
            prepared.pipeline_spec,
            handlers=[
                FlatMapIoPipelineHandlers.apply_and_drop(
                    'outbound',
                    on_output,
                    filter_type=IoPipelineHttpClientMessages.Output,
                ),
                *prepared.pipeline_spec.handlers,
            ],
        )

        #

        reader, writer = await asyncio.open_connection(prepared.parsed_url.host, prepared.parsed_url.port)

        try:
            drv = SimpleAsyncioStreamIoPipelineDriver(
                pipeline_spec,
                reader,
                writer,
            )

            drv_run_task = asyncio.create_task(drv.run())

            await drv.enqueue_waitable(IoPipelineHttpClientMessages.Request(
                prepared.full_request,
                # aggregate=...
            ))

            await drv_run_task

            response = check.not_none(response)

            stream_reader: AsyncioIoPipelineAsyncHttpClient._StreamReader
            if isinstance(response, FullIoPipelineHttpResponse):
                if response.body:
                    stream_reader = self._StaticStreamReader(response.body)
                else:
                    stream_reader = self._EmptyStreamReader()
            else:
                stream_reader = self._DriverStreamReader(drv)  # type: ignore[unreachable]

            head = check.not_none(response).head

            return AsyncStreamHttpClientResponse(
                status=head.status,
                headers=head.headers,
                request=req,
                underlying=drv,
                _stream=stream_reader,
                _closer=stream_reader.close,
            )

        finally:
            writer.close()
            await writer.wait_closed()
