# ruff: noqa: UP006 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from .....io.pipelines.core import IoPipelineHandler
from .....io.pipelines.core import IoPipelineHandlerContext
from .....io.pipelines.core import IoPipelineMessages
from .....io.pipelines.flow.types import IoPipelineFlow
from .....io.pipelines.flow.types import IoPipelineFlowMessages
from .....lite.check import check
from ....headers import HttpHeaders
from ...requests import IoFullPipelineHttpRequest
from ...responses import IoFullPipelineHttpResponse
from ...responses import IoPipelineHttpResponseHead


##


@dc.dataclass(frozen=True)
class WsgiSpec:
    app: ta.Any
    host: str = '127.0.0.1'
    port: int = 8087


##


class WsgiHandler(IoPipelineHandler):
    def __init__(self, app: ta.Any) -> None:
        super().__init__()

        self._app = app

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineMessages.InitialInput):
            ctx.feed_in(msg)

            if not IoPipelineFlow.is_auto_read_context(ctx):
                ctx.feed_out(IoPipelineFlowMessages.ReadyForInput())

            return

        if not isinstance(msg, IoFullPipelineHttpRequest):
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

        resp = IoFullPipelineHttpResponse(
            head=IoPipelineHttpResponseHead(
                status=status_code,
                reason=status_reason,
                headers=HttpHeaders(headers),
            ),
            body=body,
        )

        #

        ctx.feed_out(resp)
        ctx.feed_out(IoPipelineMessages.FinalOutput())
