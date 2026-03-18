# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import collections  # noqa
import errno
import socket
import typing as ta

from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from ....lite.check import check
from ...clients.base import HttpClientContext
from ...clients.base import HttpClientRequest
from ...clients.sync import HttpClient
from ...clients.sync import StreamHttpClientResponse
from ....io.readers import BytesReader
from ....io.readers import BytesReaders
from ...pipelines.clients.clients import IoPipelineHttpClientMessages
from ...pipelines.responses import FullIoPipelineHttpResponse
from .base import BaseIoPipelineHttpClient


##


class IoPipelineHttpClient(HttpClient, BaseIoPipelineHttpClient):
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
            raise NotImplementedError

        def read(self, n: int = -1, /) -> bytes:
            raise NotImplementedError

    #

    def _try_set_nodelay(self, sock: 'socket.socket') -> None:
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

    def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> StreamHttpClientResponse:
        prepared = self._prepare_request(req)

        sock = socket.create_connection((prepared.parsed_url.host, prepared.parsed_url.port))

        try:
            self._try_set_nodelay(sock)

            drv = SyncSocketIoPipelineDriver(prepared.pipeline_spec, sock)

            drv.enqueue(IoPipelineHttpClientMessages.Request(
                prepared.full_request,
                # aggregate=...
            ))

            response: ta.Optional[FullIoPipelineHttpResponse] = None

            while True:
                if (out := drv.next()) is not None:
                    if isinstance(out, IoPipelineHttpClientMessages.Output):
                        msg = out.msg

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

            response = check.not_none(response)

            response_reader: BytesReader

            if isinstance(response, FullIoPipelineHttpResponse):
                response_reader = BytesReaders.of_bytes(response.body)

                drv.close()
                sock.close()

                def close() -> None:
                    pass

            else:
                response_reader = self._DriverResponseReader(drv, sock)  # type: ignore[unreachable]

                def close() -> None:
                    try:
                        drv.close()
                    finally:
                        sock.close()

            #

            head = check.not_none(response).head

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
