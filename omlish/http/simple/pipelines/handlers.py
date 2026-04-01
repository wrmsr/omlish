# @omlish-lite
# ruff: noqa: UP006 UP007 UP045
import dataclasses as dc
import socket as socket_
import typing as ta

from ....io.pipelines.core import IoPipeline
from ....io.pipelines.core import IoPipelineHandler
from ....io.pipelines.core import IoPipelineHandlerContext
from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.core import IoPipelineMetadata
from ....io.pipelines.flow.types import IoPipelineFlow
from ....io.pipelines.flow.types import IoPipelineFlowMessages
from ....io.streams.utils import ByteStreamBuffers
from ....lite.check import check
from ....sockets.addresses import SocketAddress
from ....sockets.addresses import SocketAndAddress
from ...headers import HttpHeaders
from ...pipelines.requests import FullIoPipelineHttpRequest
from ...pipelines.responses import FullIoPipelineHttpResponse
from ...pipelines.responses import IoPipelineHttpResponseBodyData
from ...pipelines.responses import IoPipelineHttpResponseEnd
from ...pipelines.servers.requests import IoPipelineHttpRequestAggregatorDecoder
from ...pipelines.servers.requests import IoPipelineHttpRequestDecoder
from ...pipelines.servers.responses import IoPipelineHttpResponseEncoder
from ...pipelines.servers.responses import IoPipelineHttpResponseHead
from ..handlers import SimpleHttpHandler
from ..handlers import SimpleHttpHandlerRequest
from ..handlers import SimpleHttpHandlerResponseStreamedData


##


class SimpleHttpHandlerServerIoPipelineHandler(IoPipelineHandler):
    def __init__(self, handler: SimpleHttpHandler) -> None:
        super().__init__()

        self._handler = handler

    @dc.dataclass(frozen=True)
    class SocketAndAddressMetadata(IoPipelineMetadata):
        socket: socket_.socket
        address: SocketAddress

        @classmethod
        def of(cls, saa: SocketAndAddress) -> 'SimpleHttpHandlerServerIoPipelineHandler.SocketAndAddressMetadata':
            return cls(saa.socket, saa.address)

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.InitialInput):
            ctx.feed_in(msg)

            if not IoPipelineFlow.is_auto_read(ctx):
                ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

            return

        if not isinstance(msg, FullIoPipelineHttpRequest):
            ctx.feed_in(msg)
            return

        #

        sam = ctx.pipeline.metadata[SimpleHttpHandlerServerIoPipelineHandler.SocketAndAddressMetadata]

        handler_req = SimpleHttpHandlerRequest(
            client_address=SocketAndAddress(sam.socket, sam.address),
            method=msg.head.method,
            path=msg.head.target,
            headers=check.not_none(msg.head.parsed).headers,
            data=ByteStreamBuffers.to_bytes(msg.body),
        )

        handler_resp = self._handler(handler_req)

        try:
            headers = HttpHeaders(handler_resp.headers or {})
            new_headers: ta.Dict[str, str] = {}

            data = handler_resp.data

            if data is not None and headers.lower.get('content-length') is None:
                cl: ta.Optional[int]
                if isinstance(data, bytes):
                    cl = len(data)
                elif isinstance(data, SimpleHttpHandlerResponseStreamedData):
                    cl = data.length
                else:
                    raise TypeError(data)
                if cl is not None:
                    new_headers['Content-Length'] = str(cl)

            # if headers.lower.get('connect') is None:
            #     if h.key.lower() != 'connection':
            #         return None
            #     elif h.value.lower() == 'close':
            #         return True
            #     elif h.value.lower() == 'keep-alive':
            #         return False
            #     else:
            #         return None
            new_headers['Connection'] = 'close'  # TODO: handler_resp.close_connection

            if new_headers:
                headers = HttpHeaders({**headers, **new_headers})

            head = IoPipelineHttpResponseHead(
                status=handler_resp.status,
                reason=IoPipelineHttpResponseHead.get_reason_phrase(handler_resp.status),
                headers=headers,
            )

            if isinstance(data, (bytes, type(None))):
                resp = FullIoPipelineHttpResponse(
                    head=head,
                    body=data or b'',
                )

                ctx.feed_out(resp)

            elif isinstance(data, SimpleHttpHandlerResponseStreamedData):
                ctx.feed_out(head)

                for b in data.iter:
                    ctx.feed_out(IoPipelineHttpResponseBodyData(b))

                ctx.feed_out(IoPipelineHttpResponseEnd())

            else:
                raise TypeError(data)

            ctx.feed_out(IoPipelineMessages.FinalOutput())

        finally:
            handler_resp.close()

    #

    @classmethod
    def build_standard_pipeline_spec(
            cls,
            sock: socket_.socket,
            addr: SocketAddress,
            handler: SimpleHttpHandler,
    ) -> IoPipeline.Spec:
        return IoPipeline.Spec(
            [
                IoPipelineHttpRequestDecoder(),
                IoPipelineHttpRequestAggregatorDecoder(),
                IoPipelineHttpResponseEncoder(),
                SimpleHttpHandlerServerIoPipelineHandler(handler),
            ],
            metadata=[
                SimpleHttpHandlerServerIoPipelineHandler.SocketAndAddressMetadata(sock, addr),
            ],
        )
