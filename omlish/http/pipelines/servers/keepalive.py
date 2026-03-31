# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from ....io.pipelines.core import IoPipelineHandler
from ....io.pipelines.core import IoPipelineHandlerContext
from ....io.pipelines.core import IoPipelineMessages
from ...headers import HttpHeaders
from ...versions import HttpVersions
from ..requests import FullIoPipelineHttpRequest
from ..requests import IoPipelineHttpRequestHead
from ..responses import FullIoPipelineHttpResponse
from ..responses import IoPipelineHttpResponseEnd
from ..responses import IoPipelineHttpResponseHead


##


class IoPipelineHttpServerKeepAliveHandler(IoPipelineHandler):
    """
    Duplex handler managing HTTP/1.x connection persistence.

    Observes inbound request heads to determine keep-alive from the Connection header and HTTP version, then
    conditionally emits FinalOutput after outbound response completion. App handlers should NOT emit FinalOutput
    themselves when this handler is present.

    HTTP/1.1 defaults to keep-alive; HTTP/1.0 defaults to close.
    """

    def __init__(self) -> None:
        super().__init__()

        self._keep_alive = True
        self._idle = True

    #

    @staticmethod
    def is_request_keep_alive(head: IoPipelineHttpRequestHead) -> bool:
        if head.version >= HttpVersions.HTTP_1_1:
            return not head.headers.contains_value('connection', 'close', ignore_case=True)
        else:
            return head.headers.contains_value('connection', 'keep-alive', ignore_case=True)

    #

    def _set_response_connection_header(
            self,
            head: IoPipelineHttpResponseHead,
    ) -> IoPipelineHttpResponseHead:
        # Only set if the response doesn't already have a Connection header.
        if head.headers.lower.get('connection'):
            return head

        conn_value: ta.Optional[str] = None
        if self._keep_alive:
            if head.version < HttpVersions.HTTP_1_1:
                conn_value = 'keep-alive'
        else:
            if head.version >= HttpVersions.HTTP_1_1:
                conn_value = 'close'

        if conn_value is None:
            return head

        return IoPipelineHttpResponseHead(
            status=head.status,
            reason=head.reason,
            headers=HttpHeaders([*head.headers.raw, ('Connection', conn_value)]),
            parsed=head.parsed,
            version=head.version,
        )

    #

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, FullIoPipelineHttpRequest):
            self._idle = False
            self._keep_alive = self.is_request_keep_alive(msg.head)
            ctx.feed_in(msg)
            return

        if isinstance(msg, IoPipelineHttpRequestHead):
            self._idle = False
            self._keep_alive = self.is_request_keep_alive(msg)
            ctx.feed_in(msg)
            return

        if isinstance(msg, IoPipelineMessages.FinalInput):
            if self._idle:
                ctx.feed_in(msg)
                ctx.feed_final_output()
                return

            self._keep_alive = False
            ctx.feed_in(msg)
            return

        ctx.feed_in(msg)

    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, FullIoPipelineHttpResponse):
            msg = FullIoPipelineHttpResponse(
                head=self._set_response_connection_header(msg.head),
                body=msg.body,
            )
            ctx.feed_out(msg)
            self._idle = True
            if not self._keep_alive:
                ctx.feed_final_output()
            return

        if isinstance(msg, IoPipelineHttpResponseHead):
            msg = self._set_response_connection_header(msg)
            ctx.feed_out(msg)
            return

        if isinstance(msg, IoPipelineHttpResponseEnd):
            ctx.feed_out(msg)
            self._idle = True
            if not self._keep_alive:
                ctx.feed_final_output()
            return

        ctx.feed_out(msg)
