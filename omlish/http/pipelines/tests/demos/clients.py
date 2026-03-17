# ruff: noqa: UP006 UP045
# @omlish-lite
import collections
import dataclasses as dc
import errno
import socket
import typing as ta

from .....io.buffers import ReadableListBuffer
from .....io.pipelines.bytes.buffers import OutboundBytesBufferIoPipelineHandler
from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.core import IoPipelineHandlerFn
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver
from .....io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from .....io.pipelines.flow.stub import StubIoPipelineFlowService
from .....io.pipelines.flow.types import IoPipelineFlow
from .....io.pipelines.flow.types import IoPipelineFlowMessages
from .....io.pipelines.handlers.logs import LoggingIoPipelineHandler
from .....io.pipelines.ssl.handlers import SslIoPipelineHandler
from .....io.streams.utils import ByteStreamBuffers
from .....lite.check import check
from ....clients.base import HttpClientContext
from ....clients.base import HttpClientRequest
from ....clients.sync import HttpClient
from ....clients.sync import StreamHttpClientResponse
from ....headers import HttpHeaders
from ...clients.requests import IoPipelineHttpRequestCompressor
from ...clients.requests import IoPipelineHttpRequestEncoder
from ...clients.responses import IoPipelineHttpResponseAggregatorDecoder
from ...clients.responses import IoPipelineHttpResponseDecoder
from ...clients.responses import IoPipelineHttpResponseDecompressor
from ...requests import FullIoPipelineHttpRequest
from ...responses import FullIoPipelineHttpResponse
from ...responses import IoPipelineHttpResponseBodyData
from ...responses import IoPipelineHttpResponseEnd
from ...responses import IoPipelineHttpResponseHead
from ...responses import IoPipelineHttpResponseObject


##


PipelineHttpClientRequestOutput = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa
    IoPipelineHttpResponseObject,
    IoPipelineMessages.FinalInput,
    'PipelineHttpClientClose',
]


@dc.dataclass(frozen=True)
class PipelineHttpClientRequest:
    request: FullIoPipelineHttpRequest

    on_output: IoPipelineHandlerFn[PipelineHttpClientRequestOutput, None]

    stream: bool = False


@dc.dataclass(frozen=True)
class PipelineHttpClientClose:
    pass


#


class PipelineHttpClientHandler(IoPipelineHandler):
    _request: ta.Optional[PipelineHttpClientRequest] = None

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, PipelineHttpClientRequest):
            check.none(self._request)
            self._request = msg

            rad = check.not_none(ctx.pipeline.find_single_handler_of_type(IoPipelineHttpResponseAggregatorDecoder))
            rad.handler.set_enabled(not msg.stream)

            ctx.feed_out(msg.request)

            if (fc := ctx.services.find(IoPipelineFlow)) is not None:
                ctx.feed_out(IoPipelineFlowMessages.FlushOutput())

                if not fc.is_auto_read():
                    ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

            return

        if isinstance(msg, IoPipelineHttpResponseObject):
            request = check.not_none(self._request)

            request.on_output(ctx, msg)

            if isinstance(msg, (FullIoPipelineHttpResponse, IoPipelineHttpResponseEnd)):
                self._request = None

            return

        if isinstance(msg, (IoPipelineMessages.FinalInput, PipelineHttpClientClose)):
            if (request2 := self._request) is not None:
                self._request = None

                request2.on_output(ctx, msg)

            if isinstance(msg, IoPipelineMessages.FinalInput):
                ctx.feed_in(msg)

            ctx.feed_out(IoPipelineMessages.FinalOutput())

            return

        ctx.feed_in(msg)


#


def build_pipeline_http_client_spec(
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

            PipelineHttpClientHandler(),

            *(innermost_handlers or []),
        ],

        config=IoPipeline.Config.DEFAULT.update(
            raise_immediately=raise_immediately,
        ),

        services=[
            *([StubIoPipelineFlowService(auto_read=flow_auto_read)] if with_flow else []),
        ],
    )


##


@dc.dataclass(frozen=True)
class ParsedUrl:
    host: str
    port: int
    path: str

    is_ssl: bool = False


def parse_url(url: str) -> ParsedUrl:
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

    return ParsedUrl(
        host,
        port,
        path,
        is_ssl=is_ssl,
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


class _PreparedUrlFetch(ta.NamedTuple):
    parsed_url: ParsedUrl
    request: FullIoPipelineHttpRequest
    pipeline_spec: IoPipeline.Spec


def _prepare_url_fetch(
        url: str,
        *,
        method: str = 'GET',
        headers: ta.Optional[HttpHeaders] = None,
        **client_kwargs: ta.Any,
) -> _PreparedUrlFetch:
    parsed_url = parse_url(url)

    request = FullIoPipelineHttpRequest.simple(
        parsed_url.host,
        parsed_url.path,
        method=method,
        headers={
            'User-Agent': 'omlish-http-client/0.1',
            # 'Connection': 'close',
            **{k: v for k, vs in (headers or {}).items() for v in vs},
        },
    )

    pipeline_spec = build_pipeline_http_client_spec(
        **(dict(  # type: ignore[arg-type]
            with_ssl=True,
            ssl_kwargs=dict(
                server_side=False,
                server_hostname=parsed_url.host,
            ),
        ) if parsed_url.is_ssl else {}),

        **client_kwargs,
    )

    return _PreparedUrlFetch(
        parsed_url,
        request,
        pipeline_spec,
    )


##


async def asyncio_fetch_url(
        url: str,
        **client_kwargs: ta.Any,
) -> FullIoPipelineHttpResponse:
    puf = _prepare_url_fetch(url, **client_kwargs)

    #

    response: ta.Optional[FullIoPipelineHttpResponse] = None

    def on_output(ctx: IoPipelineHandlerContext, msg: PipelineHttpClientRequestOutput) -> None:
        if isinstance(msg, FullIoPipelineHttpResponse):
            nonlocal response
            check.none(response)
            response = msg

            ctx.pipeline.feed_in(PipelineHttpClientClose())

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

        await drv.feed_in(PipelineHttpClientRequest(
            puf.request,
            on_output,
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

    #

    response: ta.Optional[FullIoPipelineHttpResponse] = None

    def on_output(ctx: IoPipelineHandlerContext, msg: PipelineHttpClientRequestOutput) -> None:
        if isinstance(msg, FullIoPipelineHttpResponse):
            nonlocal response
            check.none(response)
            response = msg

            ctx.feed_out(IoPipelineMessages.FinalOutput())

    #

    sock = socket.create_connection((puf.parsed_url.host, puf.parsed_url.port))

    try:
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise

        #

        # Run driver to process request/response
        drv = SyncSocketIoPipelineDriver(
            puf.pipeline_spec,
            sock,
        )

        drv.enqueue(PipelineHttpClientRequest(
            puf.request,
            on_output,
        ))
        drv.loop_until_done()

    finally:
        sock.close()

    return check.not_none(response)


##


class PipelineHttpClient(HttpClient):
    class _ResponseStream:
        """Adapter that reads response body data from the pipeline driver."""

        def __init__(
                self,
                drv: SyncSocketIoPipelineDriver,
                sock: 'socket.socket',
                out_q: 'collections.deque[PipelineHttpClientRequestOutput]',
        ) -> None:
            super().__init__()

            self._drv = drv
            self._sock = sock
            self._out_q = out_q
            self._done = False

        def read1(self, n: int = -1, /) -> bytes:
            if self._done:
                return b''

            # First check if we have any queued messages from the on_output callback
            while self._out_q:
                msg = self._out_q.popleft()

                if isinstance(msg, FullIoPipelineHttpResponse):
                    # Full response - return entire body and mark done
                    self._done = True
                    from .....io.streams.utils import ByteStreamBuffers
                    return ByteStreamBuffers.to_bytes(msg.body)

                elif isinstance(msg, IoPipelineHttpResponseBodyData):
                    return msg.data

                elif isinstance(msg, (IoPipelineHttpResponseEnd, IoPipelineMessages.FinalInput)):
                    self._done = True
                    return b''

                # Skip other message types (chunks, trailers, etc.)

            # If no queued messages, pump the driver to get more
            while (out := self._drv.next()) is not None:
                if isinstance(out, FullIoPipelineHttpResponse):
                    # Full response - return entire body and mark done
                    self._done = True
                    from .....io.streams.utils import ByteStreamBuffers
                    return ByteStreamBuffers.to_bytes(out.body)

                elif isinstance(out, IoPipelineHttpResponseBodyData):
                    return out.data

                elif isinstance(out, (IoPipelineHttpResponseEnd, IoPipelineMessages.FinalInput)):
                    self._done = True
                    return b''

                # Skip other message types (chunks, trailers, etc.)

            # Pipeline stalled or ended
            self._done = True
            return b''

        def close(self) -> None:
            """Drain remaining messages and close socket."""
            if not self._done:
                # Drain remaining messages
                while not self._done:
                    self.read1()

            self._sock.close()

    def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> StreamHttpClientResponse:
        puf = _prepare_url_fetch(
            req.url,
            method=req.method or 'GET',
            headers=req.headers_,
        )

        #

        sock = socket.create_connection((puf.parsed_url.host, puf.parsed_url.port))

        try:
            try:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except OSError as e:
                if e.errno != errno.ENOPROTOOPT:
                    raise

            #

            # Run driver to process request/response
            drv = SyncSocketIoPipelineDriver(
                puf.pipeline_spec,
                sock,
            )

            out_q: collections.deque[PipelineHttpClientRequestOutput] = collections.deque()

            def on_output(h_ctx: IoPipelineHandlerContext, msg: PipelineHttpClientRequestOutput) -> None:
                out_q.append(msg)

            drv.enqueue(PipelineHttpClientRequest(
                puf.request,
                on_output,
                stream=True,
            ))

            # Get the first message - should be either FullIoPipelineHttpResponse or IoPipelineHttpResponseHead
            while True:
                while not out_q:
                    if (out := drv.next(raise_on_stall=False)) is not None:
                        out_q.append(out)
                out = out_q.popleft()
                if isinstance(out, FullIoPipelineHttpResponse):
                    # Full response received - put it back in queue for stream to read
                    out_q.append(out)
                    head = out.head
                    break

                elif isinstance(out, IoPipelineHttpResponseHead):
                    # Streaming response - head only
                    head = out
                    break

                # Skip other messages
                else:
                    raise RuntimeError('No response received from pipeline')  # noqa

            # Create streaming adapter
            stream_adapter = self._ResponseStream(drv, sock, out_q)

            return StreamHttpClientResponse(
                status=head.status,
                headers=head.headers,
                request=req,
                underlying=drv,
                _stream=ReadableListBuffer().new_buffered_reader(stream_adapter),
                _closer=stream_adapter.close,
            )

        except BaseException:
            sock.close()

            raise
