# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import dataclasses as dc
import errno
import socket
import typing as ta

from ....io.pipelines.bytes.buffers import OutboundBytesBufferIoPipelineHandler
from ....io.pipelines.core import IoPipeline
from ....io.pipelines.core import IoPipelineHandler
from ....io.pipelines.flow.stub import StubIoPipelineFlowService
from ....io.pipelines.handlers.logs import LoggingIoPipelineHandler
from ....io.pipelines.ssl.handlers import SslIoPipelineHandler
from ....lite.abstract import Abstract
from ...clients.base import BaseHttpClient
from ...clients.base import HttpClientRequest
from ...headers import HttpHeaders
from ...pipelines.clients.clients import IoPipelineHttpClientHandler
from ...pipelines.clients.requests import IoPipelineHttpRequestCompressor
from ...pipelines.clients.requests import IoPipelineHttpRequestEncoder
from ...pipelines.clients.responses import IoPipelineHttpResponseAggregatorDecoder
from ...pipelines.clients.responses import IoPipelineHttpResponseDechunker
from ...pipelines.clients.responses import IoPipelineHttpResponseDecoder
from ...pipelines.clients.responses import IoPipelineHttpResponseDecompressor
from ...pipelines.requests import FullIoPipelineHttpRequest


BaseIoPipelineHttpClientConfigT = ta.TypeVar('BaseIoPipelineHttpClientConfigT', bound='BaseIoPipelineHttpClient.Config')


##


class BaseIoPipelineHttpClient(BaseHttpClient, Abstract, ta.Generic[BaseIoPipelineHttpClientConfigT]):
    @dc.dataclass(frozen=True)
    class Config:
        connect_timeout_s: ta.Optional[float] = 3.

    def __init__(
            self,
            config: BaseIoPipelineHttpClientConfigT,
            **pipeline_kwargs: ta.Any,
    ) -> None:
        super().__init__()

        self._config = config
        self._pipeline_kwargs = pipeline_kwargs

    @property
    def config(self) -> BaseIoPipelineHttpClientConfigT:
        return self._config

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

    _aggregate_responses: bool = False  # FIXME: jank placeholder lol

    def _build_pipeline_spec(
            self,
            *,
            outermost_handlers: ta.Optional[ta.Sequence[IoPipelineHandler]] = None,
            innermost_handlers: ta.Optional[ta.Sequence[IoPipelineHandler]] = None,

            with_logging: bool = False,

            with_ssl: bool = False,
            ssl_kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,

            without_flow: bool = False,
            flow_auto_read: bool = False,

            raise_immediately: bool = False,
    ) -> IoPipeline.Spec:
        return IoPipeline.Spec(
            [
                *(outermost_handlers or []),

                *([LoggingIoPipelineHandler()] if with_logging else []),

                *([OutboundBytesBufferIoPipelineHandler()] if not without_flow else []),

                *([SslIoPipelineHandler(**(ssl_kwargs or {}))] if with_ssl else []),

                IoPipelineHttpResponseDecoder(),
                *([IoPipelineHttpResponseDechunker()] if not self._aggregate_responses else []),
                IoPipelineHttpResponseDecompressor(),
                *([IoPipelineHttpResponseAggregatorDecoder()] if self._aggregate_responses else []),

                IoPipelineHttpRequestEncoder(),
                IoPipelineHttpRequestCompressor(),

                IoPipelineHttpClientHandler(),

                *(innermost_handlers or []),
            ],

            config=IoPipeline.Config.DEFAULT.update(
                raise_immediately=raise_immediately,
            ),

            services=[
                *([StubIoPipelineFlowService(auto_read=flow_auto_read)] if not without_flow else []),
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

        data: bytes
        if isinstance(req.data, bytes):
            data = req.data
        elif isinstance(req.data, str):
            data = req.data.encode('utf-8')  # FIXME: lol
        elif req.data is None:
            data = b''
        else:
            raise TypeError(req.data)

        full_request = FullIoPipelineHttpRequest.simple(
            parsed_url.host,
            parsed_url.path,
            method=req.method_or_default,
            headers=HttpHeaders.of(req.headers_).update(
                ('User-Agent', 'omlish-http-client/0.1'),
                if_present='skip',
            ),
            body=data,
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

    #

    def _try_set_nodelay(self, sock: 'socket.socket') -> None:
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            if e.errno != errno.ENOPROTOOPT:
                raise
