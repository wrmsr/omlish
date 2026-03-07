# ruff: noqa: UP006 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.http.headers import HttpHeaders
from omlish.lite.check import check

from ....core import ChannelPipelineHandler
from ....core import ChannelPipelineHandlerContext
from ....core import ChannelPipelineMessages
from ....flow.types import ChannelPipelineFlow
from ....flow.types import ChannelPipelineFlowMessages
from ...requests import FullPipelineHttpRequest
from ...responses import FullPipelineHttpResponse
from ...responses import PipelineHttpResponseHead


##


@dc.dataclass(frozen=True)
class WsgiSpec:
    app: ta.Any
    host: str = '127.0.0.1'
    port: int = 8087


##


class WsgiHandler(ChannelPipelineHandler):
    def __init__(self, app: ta.Any) -> None:
        super().__init__()

        self._app = app

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, ChannelPipelineMessages.InitialInput):
            ctx.feed_in(msg)

            if not ChannelPipelineFlow.is_auto_read_context(ctx):
                ctx.feed_out(ChannelPipelineFlowMessages.ReadyForInput())

            return

        if not isinstance(msg, FullPipelineHttpRequest):
            ctx.feed_in(msg)
            return

        #

        environ = {
            'REQUEST_METHOD': msg.head.method,
            'PATH_INFO': msg.head.target,
        }

        #

        started_response: ta.Optional[ta.Tuple[ta.Any, ta.Any]] = None

        def start_response(status, headers):  # noqa
            nonlocal started_response
            check.none(started_response)
            started_response = (status, headers)

        #

        ret = self._app(environ, start_response)

        #

        status, headers = check.not_none(started_response)
        status_code_str, _, status_reason = status.partition(' ')
        status_code = int(status_code_str)

        #

        body: bytes
        if isinstance(ret, bytes):
            body = ret
        elif isinstance(ret, list):
            body = b''.join(ret)
        else:
            raise TypeError(ret)

        #

        resp = FullPipelineHttpResponse(
            head=PipelineHttpResponseHead(
                status=status_code,
                reason=status_reason,
                headers=HttpHeaders(headers),
            ),
            body=body,
        )

        #

        ctx.feed_out(resp)
        ctx.feed_out(ChannelPipelineMessages.FinalOutput())
