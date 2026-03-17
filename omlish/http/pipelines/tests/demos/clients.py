# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import collections  # noqa
import dataclasses as dc
import errno
import io
import socket
import typing as ta

from .....io.buffers import ReadableListBuffer  # noqa
from .....io.pipelines.bytes.buffers import OutboundBytesBufferIoPipelineHandler
from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver
from .....io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from .....io.pipelines.flow.stub import StubIoPipelineFlowService
from .....io.pipelines.handlers.flatmap import FlatMapIoPipelineHandlers
from .....io.pipelines.handlers.logs import LoggingIoPipelineHandler
from .....io.pipelines.ssl.handlers import SslIoPipelineHandler
from .....io.streams.types import BytesLike
from .....io.streams.utils import ByteStreamBuffers
from .....lite.abstract import Abstract
from .....lite.check import check
from ....clients.base import BaseHttpClient  # noqa
from ....clients.base import HttpClientContext  # noqa
from ....clients.base import HttpClientRequest  # noqa
from ....clients.sync import HttpClient  # noqa
from ....clients.sync import StreamHttpClientResponse  # noqa
from ....headers import HttpHeaders
from ...clients.clients import IoPipelineHttpClientHandler
from ...clients.clients import IoPipelineHttpClientMessages
from ...clients.requests import IoPipelineHttpRequestCompressor
from ...clients.requests import IoPipelineHttpRequestEncoder
from ...clients.responses import IoPipelineHttpResponseAggregatorDecoder
from ...clients.responses import IoPipelineHttpResponseDecoder
from ...clients.responses import IoPipelineHttpResponseDecompressor
from ...requests import FullIoPipelineHttpRequest
from ...responses import FullIoPipelineHttpResponse
from ...responses import IoPipelineHttpResponseBodyData  # noqa
from ...responses import IoPipelineHttpResponseEnd  # noqa
from ...responses import IoPipelineHttpResponseHead  # noqa


##


class BaseIoPipelineHttpClient(BaseHttpClient, Abstract):
    def __init__(self, **pipeline_kwargs: ta.Any) -> None:
        super().__init__()

        self._pipeline_kwargs = pipeline_kwargs

    #

    @dc.dataclass(frozen=True)
    class ParsedUrl:
        host: str
        port: int
        path: str

        is_ssl: bool = False

    @classmethod
    def parse_url(cls, url: str) -> ParsedUrl:
        # Parse URL (very simple - just extract host and path)
        if url.startswith('http://'):
            is_ssl = False
            url_without_scheme = url[7:]
        elif url.startswith('https://'):
            is_ssl = True
            url_without_scheme = url[8:]
        else:
            raise ValueError(url)

        if '/' in url_without_scheme:
            host, path = url_without_scheme.split('/', 1)
            path = '/' + path
        else:
            host = url_without_scheme
            path = '/'

        # Extract port if present
        if ':' in host:
            host, port_str = host.split(':', 1)
            port = int(port_str)
        else:
            if is_ssl:
                port = 443
            else:
                port = 80

        return cls.ParsedUrl(
            host,
            port,
            path,
            is_ssl=is_ssl,
        )

    #

    def _build_pipeline_spec(
            self,

            outermost_handlers: ta.Optional[ta.Sequence[IoPipelineHandler]] = None,
            innermost_handlers: ta.Optional[ta.Sequence[IoPipelineHandler]] = None,

            with_logging: bool = False,

            with_ssl: bool = False,
            ssl_kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,

            with_flow: bool = False,
            flow_auto_read: bool = False,

            raise_immediately: bool = False,
    ) -> IoPipeline.Spec:
        return IoPipeline.Spec(
            [
                *(outermost_handlers or []),

                *([LoggingIoPipelineHandler()] if with_logging else []),

                *([OutboundBytesBufferIoPipelineHandler()] if with_flow else []),

                *([SslIoPipelineHandler(**(ssl_kwargs or {}))] if with_ssl else []),

                IoPipelineHttpResponseDecoder(),
                IoPipelineHttpResponseDecompressor(),
                IoPipelineHttpResponseAggregatorDecoder(),

                IoPipelineHttpRequestEncoder(),
                IoPipelineHttpRequestCompressor(),

                IoPipelineHttpClientHandler(),

                *(innermost_handlers or []),
            ],

            config=IoPipeline.Config.DEFAULT.update(
                raise_immediately=raise_immediately,
            ),

            services=[
                *([StubIoPipelineFlowService(auto_read=flow_auto_read)] if with_flow else []),
            ],
        )

    #

    @dc.dataclass(frozen=True)
    class _PreparedRequest:
        parsed_url: 'BaseIoPipelineHttpClient.ParsedUrl'
        full_request: FullIoPipelineHttpRequest
        pipeline_spec: IoPipeline.Spec

    def _prepare_request(
            self,
            req: HttpClientRequest,
            **pipeline_kwargs: ta.Any,
    ) -> _PreparedRequest:
        parsed_url = self.parse_url(req.url)

        full_request = FullIoPipelineHttpRequest.simple(
            parsed_url.host,
            parsed_url.path,
            method=req.method_or_default,
            headers=HttpHeaders.of(req.headers_).update(
                ('User-Agent', 'omlish-http-client/0.1'),
                if_present='skip',
            ),
        )

        pipeline_spec = self._build_pipeline_spec(
            **(dict(  # type: ignore[arg-type]
                with_ssl=True,
                ssl_kwargs=dict(
                    server_side=False,
                    server_hostname=parsed_url.host,
                ),
            ) if parsed_url.is_ssl else {}),

            **{
                **self._pipeline_kwargs,
                **pipeline_kwargs,
            },
        )

        return self._PreparedRequest(
            parsed_url,
            full_request,
            pipeline_spec,
        )


##


def print_full_response(response: FullIoPipelineHttpResponse) -> None:
    """Print the accumulated response."""

    head = response.head
    body = ByteStreamBuffers.to_bytes(response.body)

    print(f'HTTP/{head.version.major}.{head.version.minor} {head.status} {head.reason}')
    print()

    # Print headers
    for name, value in head.headers.raw:
        print(f'{name}: {value}')

    print()

    # Print body (decoded if text)
    try:
        print(body.decode('utf-8'))
    except UnicodeDecodeError:
        print(f'<binary body: {len(body)} bytes>')


##


async def asyncio_fetch_url(
        url: str,
        **client_kwargs: ta.Any,
) -> FullIoPipelineHttpResponse:
    puf = _prepare_url_fetch(url, **client_kwargs)

    #

    response: ta.Optional[FullIoPipelineHttpResponse] = None

    def on_output(ctx: IoPipelineHandlerContext, out: IoPipelineHttpClientMessages.Output) -> None:
        msg = out.msg

        if isinstance(msg, FullIoPipelineHttpResponse):
            nonlocal response
            check.none(response)
            response = msg

            ctx.pipeline.feed_in(IoPipelineHttpClientMessages.Close())

        elif isinstance(msg, (IoPipelineMessages.FinalInput, IoPipelineHttpClientMessages.Close)):
            pass

        else:
            raise TypeError(msg)

    puf = dc.replace(
        puf,
        pipeline_spec=dc.replace(
            puf.pipeline_spec,
            handlers=[
                FlatMapIoPipelineHandlers.apply_and_drop(
                    'outbound',
                    on_output,
                    filter_type=IoPipelineHttpClientMessages.Output,
                ),
                *puf.pipeline_spec.handlers,
            ],
        ),
    )

    #

    import asyncio

    reader, writer = await asyncio.open_connection(puf.parsed_url.host, puf.parsed_url.port)

    try:
        drv = SimpleAsyncioStreamIoPipelineDriver(
            puf.pipeline_spec,
            reader,
            writer,
        )

        drv_run_task = asyncio.create_task(drv.run())

        await drv.enqueue_waitable(IoPipelineHttpClientMessages.Request(
            puf.request,
        ))

        await drv_run_task

    finally:
        writer.close()
        await writer.wait_closed()

    return check.not_none(response)


##


def sync_fetch_url(
        url: str,
        **client_kwargs: ta.Any,
) -> FullIoPipelineHttpResponse:
    puf = _prepare_url_fetch(url, **client_kwargs)

    sock = socket.create_connection((puf.parsed_url.host, puf.parsed_url.port))

    try:
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

        #

        drv = SyncSocketIoPipelineDriver(
            puf.pipeline_spec,
            sock,
        )

        drv.enqueue(IoPipelineHttpClientMessages.Request(
            puf.request,
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
                        raise TypeError(out)

                else:
                    raise TypeError(out)

            if not drv.pipeline.is_ready:
                break

    finally:
        sock.close()

    return check.not_none(response)


##


class IoPipelineHttpClient(HttpClient, BaseIoPipelineHttpClient):
    class _ResponseStream(Abstract):
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

    class _EmptyResponseStream(_ResponseStream):
        def read1(self, n: int = -1, /) -> bytes:
            return b''

        def read(self, n: int = -1, /) -> bytes:
            return b''

    class _StaticResponseStream(_ResponseStream):
        def __init__(self, b: BytesLike) -> None:
            self._r = io.BytesIO(b)

        def read1(self, n: int = -1, /) -> bytes:
            return self._r.read1(n)

        def read(self, n: int = -1, /) -> bytes:
            return self._r.read1(n)

    class _DriverResponseStream(_ResponseStream):
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

            drv.enqueue(IoPipelineHttpClientMessages.Request(prepared.full_request))

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

            response_stream: IoPipelineHttpClient._ResponseStream
            if isinstance(response, FullIoPipelineHttpResponse):
                if response.body:
                    response_stream = self._StaticResponseStream(response.body)
                else:
                    response_stream = self._EmptyResponseStream()
            else:
                response_stream = self._DriverResponseStream(drv, sock)  # type: ignore[unreachable]

            head = check.not_none(response).head

            return StreamHttpClientResponse(
                status=head.status,
                headers=head.headers,
                request=req,
                underlying=drv,
                _stream=response_stream,
                _closer=response_stream.close,
            )

        except BaseException:
            sock.close()

            raise
