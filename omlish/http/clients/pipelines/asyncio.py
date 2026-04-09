# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import asyncio
import dataclasses as dc
import io
import typing as ta

from ....asyncs.asyncio.timeouts import asyncio_maybe_timeout
from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.drivers.asyncio2 import PollAsyncioStreamIoPipelineDriver
from ....io.readers import AsyncBytesReader
from ....io.readers import AsyncBytesReaders
from ....io.streams.utils import ByteStreamBuffers
from ....lite.check import check
from ...clients.asyncs import AsyncHttpClient
from ...clients.asyncs import AsyncStreamHttpClientResponse
from ...clients.base import HttpClientContext
from ...clients.base import HttpClientRequest
from ...pipelines.clients.clients import IoPipelineHttpClientMessages
from ...pipelines.responses import FullIoPipelineHttpResponse
from ...pipelines.responses import IoPipelineHttpResponseBodyData
from ...pipelines.responses import IoPipelineHttpResponseEnd
from ...pipelines.responses import IoPipelineHttpResponseHead
from ..base import HttpClientError
from .base import BaseIoPipelineHttpClient


##


class AsyncioIoPipelineAsyncHttpClient(AsyncHttpClient, BaseIoPipelineHttpClient['AsyncioIoPipelineAsyncHttpClient.Config']):  # noqa
    @dc.dataclass(frozen=True)
    class Config(BaseIoPipelineHttpClient.Config):
        DEFAULT: ta.ClassVar['AsyncioIoPipelineAsyncHttpClient.Config']

    Config.DEFAULT = Config()

    def __init__(
            self,
            config: Config = Config.DEFAULT,
            **pipeline_kwargs: ta.Any,
    ) -> None:
        super().__init__(
            config,
            **pipeline_kwargs,
        )

    #

    class _DriverResponseReader:
        def __init__(
                self,
                drv: PollAsyncioStreamIoPipelineDriver,
        ) -> None:
            super().__init__()

            self._drv = drv

        async def read1(self, n: int = -1, /) -> bytes:
            while True:
                out = check.not_none(await self._drv.next())

                if isinstance(out, IoPipelineHttpClientMessages.Output):
                    msg = out.msg

                    if isinstance(msg, IoPipelineHttpResponseBodyData):
                        return ByteStreamBuffers.to_bytes(msg.data)

                    elif isinstance(msg, (
                            IoPipelineHttpResponseEnd,
                            IoPipelineMessages.FinalInput,
                            IoPipelineHttpClientMessages.Close,
                    )):
                        return b''

                    else:
                        raise TypeError(out)  # noqa

                else:
                    raise TypeError(out)  # noqa

        async def read(self, n: int = -1, /) -> bytes:
            buf = io.BytesIO()

            while b := await self.read1(n):
                buf.write(b)

            return buf.getvalue()

    #

    async def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> AsyncStreamHttpClientResponse:
        try:
            prepared = self._prepare_request(req)

            reader, writer = await asyncio_maybe_timeout(
                asyncio.open_connection(
                    prepared.parsed_url.host,
                    prepared.parsed_url.port,
                ),
                self._config.connect_timeout_s,
            )

            try:
                drv = PollAsyncioStreamIoPipelineDriver(
                    prepared.pipeline_spec,
                    reader,
                    writer,
                )

                drv.enqueue(IoPipelineHttpClientMessages.Request(
                    prepared.full_request,
                    # aggregate=...
                ))

                response: ta.Union[IoPipelineHttpResponseHead, FullIoPipelineHttpResponse, None] = None

                while True:
                    if (out := await drv.next()) is not None:
                        if isinstance(out, IoPipelineHttpClientMessages.Output):
                            msg = out.msg

                            if isinstance(msg, IoPipelineHttpResponseHead):
                                check.none(response)
                                response = msg

                                break

                            if isinstance(msg, FullIoPipelineHttpResponse):
                                check.none(response)
                                response = msg

                                drv.enqueue(IoPipelineHttpClientMessages.Close())

                            elif isinstance(msg, (IoPipelineMessages.FinalInput, IoPipelineHttpClientMessages.Close)):
                                pass

                            else:
                                raise TypeError(out)  # noqa

                        else:
                            raise TypeError(out)  # noqa

                    if not drv.pipeline.is_ready:
                        break

                #

                response = check.not_none(response)  # type: ignore[assignment]

                head: IoPipelineHttpResponseHead

                response_reader: AsyncBytesReader

                if isinstance(response, FullIoPipelineHttpResponse):
                    head = check.not_none(response).head

                    response_reader = AsyncBytesReaders.of_bytes(response.body)

                    await drv.close()
                    writer.close()
                    await writer.wait_closed()

                    async def close() -> None:
                        pass

                elif isinstance(response, IoPipelineHttpResponseHead):
                    head = response

                    response_reader = self._DriverResponseReader(drv)

                    async def close() -> None:
                        try:
                            await drv.close()
                        finally:
                            writer.close()
                            await writer.wait_closed()

                else:
                    raise TypeError(response)  # noqa

                #

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

        except asyncio.CancelledError:
            raise

        except Exception as e:
            raise HttpClientError from e
