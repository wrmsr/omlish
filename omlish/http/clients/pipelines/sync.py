# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import collections  # noqa
import dataclasses as dc
import io
import socket
import typing as ta

from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from ....io.readers import BytesReader
from ....io.readers import BytesReaders
from ....io.streams.utils import ByteStreamBuffers
from ....lite.check import check
from ...clients.base import HttpClientContext
from ...clients.base import HttpClientRequest
from ...clients.sync import HttpClient
from ...clients.sync import StreamHttpClientResponse
from ...pipelines.clients.clients import IoPipelineHttpClientMessages
from ...pipelines.responses import FullIoPipelineHttpResponse
from ...pipelines.responses import IoPipelineHttpResponseBodyData
from ...pipelines.responses import IoPipelineHttpResponseEnd
from ...pipelines.responses import IoPipelineHttpResponseHead
from ..base import HttpClientError
from .base import BaseIoPipelineHttpClient


##


class IoPipelineHttpClient(HttpClient, BaseIoPipelineHttpClient['IoPipelineHttpClient.Config']):
    @dc.dataclass(frozen=True)
    class Config(BaseIoPipelineHttpClient.Config):
        DEFAULT: ta.ClassVar['IoPipelineHttpClient.Config']

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
                drv: SyncSocketIoPipelineDriver,
                sock: 'socket.socket',
        ) -> None:
            super().__init__()

            self._drv = drv
            self._sock = sock

            self._done = False

        def read1(self, n: int = -1, /) -> bytes:
            while True:
                out = check.not_none(self._drv.next())

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

        def read(self, n: int = -1, /) -> bytes:
            buf = io.BytesIO()

            while b := self.read1(n):
                buf.write(b)

            return buf.getvalue()

    #

    def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> StreamHttpClientResponse:
        try:
            prepared = self._prepare_request(req)

            sock = socket.create_connection(
                (prepared.parsed_url.host, prepared.parsed_url.port),
                **(dict(timeout=self._config.connect_timeout_s) if self._config.connect_timeout_s is not None else {}),  # type: ignore[arg-type]  # noqa
            )

            try:
                self._try_set_nodelay(sock)

                drv = SyncSocketIoPipelineDriver(prepared.pipeline_spec, sock)

                drv.enqueue(IoPipelineHttpClientMessages.Request(
                    prepared.full_request,
                    # aggregate=...
                ))

                response: ta.Union[IoPipelineHttpResponseHead, FullIoPipelineHttpResponse, None] = None

                while True:
                    if (out := drv.next()) is not None:
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

                response_reader: BytesReader

                if isinstance(response, FullIoPipelineHttpResponse):
                    head = check.not_none(response).head

                    response_reader = BytesReaders.of_bytes(response.body)

                    drv.close()
                    sock.close()

                    def close() -> None:
                        pass

                elif isinstance(response, IoPipelineHttpResponseHead):
                    head = response

                    response_reader = self._DriverResponseReader(drv, sock)

                    def close() -> None:
                        try:
                            drv.close()
                        finally:
                            sock.close()

                else:
                    raise TypeError(response)  # noqa

                #

                return StreamHttpClientResponse(
                    status=head.status,
                    headers=head.headers,
                    request=req,
                    underlying=drv,
                    _stream=response_reader,
                    _closer=close,
                )

            except BaseException:
                sock.close()

                raise

        except Exception as e:
            raise HttpClientError from e
