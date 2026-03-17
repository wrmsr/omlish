# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import collections  # noqa
import errno
import io
import socket
import typing as ta

from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from ....io.streams.types import BytesLike
from ....lite.abstract import Abstract
from ....lite.check import check
from ...clients.base import HttpClientContext
from ...clients.base import HttpClientRequest
from ...clients.sync import HttpClient
from ...clients.sync import StreamHttpClientResponse
from ...pipelines.clients.clients import IoPipelineHttpClientMessages
from ...pipelines.responses import FullIoPipelineHttpResponse
from .base import BaseIoPipelineHttpClient


##


class IoPipelineHttpClient(HttpClient, BaseIoPipelineHttpClient):
    class _StreamReader(Abstract):
        @abc.abstractmethod
        def read1(self, n: int = -1, /) -> bytes:
            raise NotImplementedError

        @abc.abstractmethod
        def read(self, n: int = -1, /) -> bytes:
            raise NotImplementedError

        def readall(self) -> bytes:
            return self.read()

        def close(self) -> None:
            pass

    class _EmptyStreamReader(_StreamReader):
        def read1(self, n: int = -1, /) -> bytes:
            return b''

        def read(self, n: int = -1, /) -> bytes:
            return b''

    class _StaticStreamReader(_StreamReader):
        def __init__(self, b: BytesLike) -> None:
            self._r = io.BytesIO(b)

        def read1(self, n: int = -1, /) -> bytes:
            return self._r.read1(n)

        def read(self, n: int = -1, /) -> bytes:
            return self._r.read1(n)

    class _DriverStreamReader(_StreamReader):
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

        def readall(self) -> bytes:
            raise NotImplementedError

        def close(self) -> None:
            try:
                self._drv.close()
            finally:
                self._sock.close()

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

            response = check.not_none(response)

            stream_reader: IoPipelineHttpClient._StreamReader
            if isinstance(response, FullIoPipelineHttpResponse):
                if response.body:
                    stream_reader = self._StaticStreamReader(response.body)
                else:
                    stream_reader = self._EmptyStreamReader()
            else:
                stream_reader = self._DriverStreamReader(drv, sock)  # type: ignore[unreachable]

            head = check.not_none(response).head

            return StreamHttpClientResponse(
                status=head.status,
                headers=head.headers,
                request=req,
                underlying=drv,
                _stream=stream_reader,
                _closer=stream_reader.close,
            )

        except BaseException:
            sock.close()

            raise
