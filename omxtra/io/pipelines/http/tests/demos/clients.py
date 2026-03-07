# ruff: noqa: UP006 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.io.streams.utils import ByteStreamBuffers
from omlish.lite.check import check

from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import ChannelPipelineHandlerFn
from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....drivers.asyncio import SimpleAsyncioStreamPipelineChannelDriver
from ....drivers.sync import SyncSocketPipelineChannelDriver
from ....flow.stub import StubChannelPipelineFlow
from ....flow.types import ChannelPipelineFlowMessages
from ....handlers.logs import LoggingChannelPipelineHandler
from ....ssl.handlers import SslChannelPipelineHandler
from ...client.requests import PipelineHttpRequestEncoder
from ...client.responses import PipelineHttpResponseAggregatorDecoder
from ...client.responses import PipelineHttpResponseDecoder
from ...client.responses import PipelineHttpResponseDecompressor
from ...requests import FullPipelineHttpRequest
from ...responses import FullPipelineHttpResponse
from ...responses import PipelineHttpResponseEnd
from ...responses import PipelineHttpResponseObject


##


HttpClientRequestOutput = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa
    PipelineHttpResponseObject,
    ChannelPipelineMessages.FinalInput,
    'HttpClientClose',
]


@dc.dataclass(frozen=True)
class HttpClientRequest:
    request: FullPipelineHttpRequest

    on_output: ChannelPipelineHandlerFn[HttpClientRequestOutput, None]

    stream: bool = False


@dc.dataclass(frozen=True)
class HttpClientClose:
    pass


#


class HttpClientHandler(ChannelPipelineHandler):
    _request: ta.Optional[HttpClientRequest] = None

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, HttpClientRequest):
            check.none(self._request)
            self._request = msg

            rad = check.not_none(ctx.pipeline.find_single_handler_of_type(PipelineHttpResponseAggregatorDecoder))
            rad.handler.set_enabled(not msg.stream)

            ctx.feed_out(msg.request)

            if not StubChannelPipelineFlow.is_auto_read_context(ctx):
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

            return

        if isinstance(msg, PipelineHttpResponseObject):
            request = check.not_none(self._request)

            request.on_output(ctx, msg)

            if isinstance(msg, (FullPipelineHttpResponse, PipelineHttpResponseEnd)):
                self._request = None

            return

        if isinstance(msg, (ChannelPipelineMessages.FinalInput, HttpClientClose)):
            if (request2 := self._request) is not None:
                self._request = None

                request2.on_output(ctx, msg)

            if isinstance(msg, ChannelPipelineMessages.FinalInput):
                ctx.feed_in(msg)

            ctx.feed_out(ChannelPipelineMessages.FinalOutput())

            return

        ctx.feed_in(msg)


#


def build_http_client(
        outermost_handlers: ta.Optional[ta.Sequence[ChannelPipelineHandler]] = None,
        innermost_handlers: ta.Optional[ta.Sequence[ChannelPipelineHandler]] = None,

        with_logging: bool = False,

        with_ssl: bool = False,
        ssl_kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,

        with_gzip: bool = False,

        with_flow: bool = False,
        flow_auto_read: bool = False,

        raise_immediately: bool = False,
) -> PipelineChannel.Spec:
    return PipelineChannel.Spec(
        [
            *(outermost_handlers or []),

            *([LoggingChannelPipelineHandler()] if with_logging else []),

            *([SslChannelPipelineHandler(**(ssl_kwargs or {}))] if with_ssl else []),

            PipelineHttpResponseDecoder(),
            *([PipelineHttpResponseDecompressor()] if with_gzip else []),
            PipelineHttpResponseAggregatorDecoder(),

            PipelineHttpRequestEncoder(),

            HttpClientHandler(),

            *(innermost_handlers or []),
        ],

        config=PipelineChannel.Config.DEFAULT.update_pipeline(
            raise_immediately=raise_immediately,
        ),

        services=[
            *([StubChannelPipelineFlow(auto_read=flow_auto_read)] if with_flow else []),
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


def print_full_response(response: FullPipelineHttpResponse) -> None:
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
    request: FullPipelineHttpRequest
    pipeline_spec: PipelineChannel.Spec


def _prepare_url_fetch(
        url: str,
        **client_kwargs: ta.Any,
) -> _PreparedUrlFetch:
    parsed_url = parse_url(url)

    request = FullPipelineHttpRequest.simple(
        parsed_url.host,
        parsed_url.path,
        headers={
            'User-Agent': 'omlish-http-client/0.1',
            # 'Connection': 'close',
        },
    )

    pipeline_spec = build_http_client(
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
) -> FullPipelineHttpResponse:
    puf = _prepare_url_fetch(url, **client_kwargs)

    #

    response: ta.Optional[FullPipelineHttpResponse] = None

    def on_output(ctx: ChannelPipelineHandlerContext, msg: HttpClientRequestOutput) -> None:
        if isinstance(msg, FullPipelineHttpResponse):
            nonlocal response
            check.none(response)
            response = msg

            ctx.channel.feed_in(HttpClientClose())

    #

    import asyncio

    reader, writer = await asyncio.open_connection(puf.parsed_url.host, puf.parsed_url.port)

    try:
        drv = SimpleAsyncioStreamPipelineChannelDriver(
            puf.pipeline_spec,
            reader,
            writer,
        )

        drv_run_task = asyncio.create_task(drv.run())

        await drv.feed_in(HttpClientRequest(
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
) -> FullPipelineHttpResponse:
    puf = _prepare_url_fetch(url, **client_kwargs)

    #

    response: ta.Optional[FullPipelineHttpResponse] = None

    def on_output(ctx: ChannelPipelineHandlerContext, msg: HttpClientRequestOutput) -> None:
        if isinstance(msg, FullPipelineHttpResponse):
            nonlocal response
            check.none(response)
            response = msg

            ctx.channel.feed_in(HttpClientClose())

    #

    import errno
    import socket

    sock = socket.create_connection((puf.parsed_url.host, puf.parsed_url.port))

    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except OSError as e:
        if e.errno != errno.ENOPROTOOPT:
            raise

    #

    try:
        # Run driver to process request/response
        drv = SyncSocketPipelineChannelDriver(
            puf.pipeline_spec,
            sock,
        )

        drv.run(HttpClientRequest(
            puf.request,
            on_output,
        ))

    finally:
        sock.close()

    #

    return check.not_none(response)
