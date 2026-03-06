# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio
import dataclasses as dc
import typing as ta

from omlish.lite.check import check
from omlish.io.streams.utils import ByteStreamBuffers

from ....drivers.asyncio import SimpleAsyncioStreamPipelineChannelDriver
from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineMessages
from ....core import PipelineChannel
from ....flow.stub import StubChannelPipelineFlow
from ....flow.types import ChannelPipelineFlowMessages
from ....handlers.flatmap import InboundFlatMapChannelPipelineHandler
from ....handlers.flatmap import FlatMapChannelPipelineHandlers
from ....handlers.flatmap import FlatMapChannelPipelineHandlerFns
from ....handlers.logs import LoggingChannelPipelineHandler
from ....ssl.handlers import SslChannelPipelineHandler
from ...client.requests import PipelineHttpRequestEncoder
from ...client.responses import PipelineHttpResponseDecoder
from ...client.responses import PipelineHttpResponseDecompressor
from ...requests import FullPipelineHttpRequest
from ...responses import FullPipelineHttpResponse
from ....handlers.queues import InboundQueueChannelPipelineHandler
from ...client.responses import PipelineHttpResponseAggregatorDecoder


##


def build_http_client(
        *,
        outermost_handlers: ta.Optional[ta.Sequence[ChannelPipelineHandler]] = None,
        innermost_handlers: ta.Optional[ta.Sequence[ChannelPipelineHandler]] = None,

        with_logging: bool = False,

        with_ssl: bool = False,
        ssl_kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,

        with_gzip: bool = False,

        with_aggregator: bool = False,

        with_flow: bool = False,
        flow_auto_read: bool = False,

        raise_immediately: bool = False,
) -> PipelineChannel.Spec:
    return PipelineChannel.Spec(
        [
            *(outermost_handlers or []),

            *([LoggingChannelPipelineHandler()] if with_logging else []),

            *([SslChannelPipelineHandler(**(ssl_kwargs or {}))] if with_ssl else []),

            PipelineHttpRequestEncoder(),
            InboundFlatMapChannelPipelineHandler(
                (ffn := FlatMapChannelPipelineHandlerFns).filter_type(
                    FullPipelineHttpRequest,
                    ffn.compose(
                        *([ffn.inject(after=[ChannelPipelineFlowMessages.ReadyForInput()])] if with_flow and not flow_auto_read else []),  # noqa,
                        ffn.feed_out(),
                        ffn.drop(),
                    ),
                ),
            ),

            PipelineHttpResponseDecoder(),
            *([PipelineHttpResponseDecompressor()] if with_gzip else []),
            *([PipelineHttpResponseAggregatorDecoder()] if with_aggregator else []),

            InboundFlatMapChannelPipelineHandler(
                ffn.filter_type(
                    FullPipelineHttpResponse,
                    ffn.concat(
                        ffn.compose(
                            lambda _ctx, _msg: [ChannelPipelineMessages.FinalOutput()],
                            ffn.feed_out(),
                            ffn.drop(),
                        ),
                        ffn.nop(),
                    ),
                ),
            ),

            *([FlatMapChannelPipelineHandlers.drop('inbound', filter_type=ChannelPipelineFlowMessages.FlushInput)] if with_flow else []),  # noqa

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


def parse_url(url: str) -> ParsedUrl:
    # Parse URL (very simple - just extract host and path)
    if url.startswith('http://'):
        ssl = False
        url_without_scheme = url[7:]
    elif url.startswith('https://'):
        ssl = True
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
        if ssl:
            port = 443
        else:
            port = 80

    return ParsedUrl(
        host,
        port,
        path,
    )


##


def print_full_response(response: FullPipelineHttpResponse) -> None:
    """Print the accumulated response."""

    head = response.head
    body = ByteStreamBuffers.any_to_bytes(response.body)

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
) -> FullPipelineHttpResponse:
    parsed_url = parse_url(url)

    # Connect
    reader, writer = await asyncio.open_connection(parsed_url.host, parsed_url.port)

    try:
        # Send request
        request = FullPipelineHttpRequest.simple(
            parsed_url.host,
            parsed_url.path,
            headers={
                'User-Agent': 'omlish-http-client/0.1',
            },
        )

        response_queue = InboundQueueChannelPipelineHandler(
            filter_type=FullPipelineHttpResponse,
        )

        pipeline_spec = build_http_client(
            innermost_handlers=[response_queue],

            with_aggregator=True,

            **client_kwargs,
        )

        # Run driver to process request/response
        drv = SimpleAsyncioStreamPipelineChannelDriver(
            pipeline_spec,
            reader,
            writer,
        )

        drv_run_task = asyncio.create_task(drv.run())

        await drv.feed_in(request)

        await drv_run_task

    finally:
        writer.close()
        await writer.wait_closed()

    out = check.single(response_queue.drain())
    return check.isinstance(out, FullPipelineHttpResponse)
