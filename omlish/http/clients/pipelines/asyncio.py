# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import asyncio
import dataclasses as dc
import typing as ta

from ....io.pipelines.core import IoPipelineHandlerContext
from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.drivers.asyncio import LoopAsyncioStreamIoPipelineDriver
from ....io.pipelines.handlers.flatmap import FlatMapIoPipelineHandlers
from ....io.readers import AsyncBytesReader
from ....io.readers import AsyncBytesReaders
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
    class _DriverResponseReader:
        def __init__(
                self,
                drv: LoopAsyncioStreamIoPipelineDriver,
        ) -> None:
            super().__init__()

            self._drv = drv

            self._done = False

        async def read1(self, n: int = -1, /) -> bytes:
            raise NotImplementedError

        async def read(self, n: int = -1, /) -> bytes:
            raise NotImplementedError

    #

    _aggregate_responses: bool = True

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
            drv = LoopAsyncioStreamIoPipelineDriver(
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

            #

            response = check.not_none(response)

            response_reader: AsyncBytesReader

            if isinstance(response, FullIoPipelineHttpResponse):
                response_reader = AsyncBytesReaders.of_bytes(response.body)

                drv.pipeline.destroy()

                writer.close()
                await writer.wait_closed()

                async def close() -> None:
                    pass

            else:
                response_reader = self._DriverResponseReader(drv)  # type: ignore[unreachable]

                async def close() -> None:
                    try:
                        drv.pipeline.destroy()
                    finally:
                        writer.close()
                        await writer.wait_closed()

            #

            head = check.not_none(response).head

            return AsyncStreamHttpClientResponse(
                status=head.status,
                headers=head.headers,
                request=req,
                underlying=drv,
                _stream=response_reader,
                _closer=close,
            )

        except BaseException:
            writer.close()
            await writer.wait_closed()

            raise
