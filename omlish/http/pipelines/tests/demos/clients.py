# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import collections  # noqa
import dataclasses as dc
import errno
import socket
import typing as ta

from .....io.buffers import ReadableListBuffer  # noqa
from .....io.pipelines.bytes.buffers import OutboundBytesBufferIoPipelineHandler
from .....io.pipelines.core import IoPipeline
from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.handlers.flatmap import FlatMapIoPipelineHandlers
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.drivers.asyncio import SimpleAsyncioStreamIoPipelineDriver
from .....io.pipelines.drivers.sync import SyncSocketIoPipelineDriver
from .....io.pipelines.flow.stub import StubIoPipelineFlowService
from .....io.pipelines.handlers.logs import LoggingIoPipelineHandler
from .....io.pipelines.ssl.handlers import SslIoPipelineHandler
from .....io.streams.utils import ByteStreamBuffers
from .....lite.check import check
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


def build_io_pipeline_http_client_spec(
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


@dc.dataclass(frozen=True)
class _PreparedUrlFetch:
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

    pipeline_spec = build_io_pipeline_http_client_spec(
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

        # Run driver to process request/response
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


# class PipelineHttpClient(HttpClient):
#     class _ResponseStream:
#         """Adapter that reads response body data from the pipeline driver."""
#
#         def __init__(
#                 self,
#                 drv: SyncSocketIoPipelineDriver,
#                 sock: 'socket.socket',
#                 out_q: 'collections.deque[IoPipelineHttpClientRequestOutput]',
#         ) -> None:
#             super().__init__()
#
#             self._drv = drv
#             self._sock = sock
#             self._out_q = out_q
#             self._done = False
#
#         def read1(self, n: int = -1, /) -> bytes:
#             if self._done:
#                 return b''
#
#             # First check if we have any queued messages from the on_output callback
#             while self._out_q:
#                 msg = self._out_q.popleft()
#
#                 if isinstance(msg, FullIoPipelineHttpResponse):
#                     # Full response - return entire body and mark done
#                     self._done = True
#                     return ByteStreamBuffers.to_bytes(msg.body)
#
#                 elif isinstance(msg, IoPipelineHttpResponseBodyData):
#                     return msg.data
#
#                 elif isinstance(msg, (IoPipelineHttpResponseEnd, IoPipelineMessages.FinalInput)):
#                     self._done = True
#                     return b''
#
#                 # Skip other message types (chunks, trailers, etc.)
#
#             # If no queued messages, pump the driver to get more
#             while (out := self._drv.next()) is not None:
#                 if isinstance(out, FullIoPipelineHttpResponse):
#                     # Full response - return entire body and mark done
#                     self._done = True
#                     return ByteStreamBuffers.to_bytes(out.body)
#
#                 elif isinstance(out, IoPipelineHttpResponseBodyData):
#                     return out.data
#
#                 elif isinstance(out, (IoPipelineHttpResponseEnd, IoPipelineMessages.FinalInput)):
#                     self._done = True
#                     return b''
#
#                 # Skip other message types (chunks, trailers, etc.)
#
#             # Pipeline stalled or ended
#             self._done = True
#             return b''
#
#         def close(self) -> None:
#             try:
#                 self._drv.close()
#             finally:
#                 self._sock.close()
#
#     def _stream_request(self, ctx: HttpClientContext, req: HttpClientRequest) -> StreamHttpClientResponse:
#         puf = _prepare_url_fetch(
#             req.url,
#             method=req.method or 'GET',
#             headers=req.headers_,
#         )
#
#         #
#
#         sock = socket.create_connection((puf.parsed_url.host, puf.parsed_url.port))
#
#         try:
#             try:
#                 sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
#             except OSError as e:
#                 if e.errno != errno.ENOPROTOOPT:
#                     raise
#
#             #
#
#             # Run driver to process request/response
#             drv = SyncSocketIoPipelineDriver(
#                 puf.pipeline_spec,
#                 sock,
#             )
#
#             out_q: collections.deque[IoPipelineHttpClientRequestOutput] = collections.deque()
#
#             def on_output(h_ctx: IoPipelineHandlerContext, msg: IoPipelineHttpClientRequestOutput) -> None:
#                 out_q.append(msg)
#
#             drv.enqueue(IoPipelineHttpClientRequest(
#                 puf.request,
#                 on_output,
#                 stream=True,
#             ))
#
#             # Get the first message - should be either FullIoPipelineHttpResponse or IoPipelineHttpResponseHead
#             while True:
#                 while not out_q:
#                     if (out := drv.next()) is not None:
#                         out_q.append(out)
#
#                 out = out_q.popleft()
#
#                 if isinstance(out, FullIoPipelineHttpResponse):
#                     # Full response received - put it back in queue for stream to read
#                     out_q.append(out)
#                     head = out.head
#                     break
#
#                 elif isinstance(out, IoPipelineHttpResponseHead):
#                     # Streaming response - head only
#                     head = out
#                     break
#
#                 else:
#                     raise TypeError(out)  # noqa
#
#             # Create streaming adapter
#             stream_adapter = self._ResponseStream(drv, sock, out_q)
#
#             return StreamHttpClientResponse(
#                 status=head.status,
#                 headers=head.headers,
#                 request=req,
#                 underlying=drv,
#                 _stream=ReadableListBuffer().new_buffered_reader(stream_adapter),
#                 _closer=stream_adapter.close,
#             )
#
#         except BaseException:
#             sock.close()
#
#             raise
