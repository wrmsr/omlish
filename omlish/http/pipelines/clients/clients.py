# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ....io.pipelines.core import IoPipelineHandler
from ....io.pipelines.core import IoPipelineHandlerContext
from ....io.pipelines.core import IoPipelineMessages
from ....io.pipelines.flow.types import IoPipelineFlow
from ....lite.check import check
from ....lite.namespaces import NamespaceClass
from ..requests import FullIoPipelineHttpRequest
from ..responses import FullIoPipelineHttpResponse
from ..responses import IoPipelineHttpResponseEnd
from ..responses import IoPipelineHttpResponseObject
from .responses import IoPipelineHttpResponseAggregatorDecoder


##


class IoPipelineHttpClientMessages(NamespaceClass):
    @dc.dataclass(frozen=True)
    class Request(IoPipelineMessages.NeverOutbound):
        request: FullIoPipelineHttpRequest

        aggregate: ta.Union[bool, ta.Literal['unless_chunked'], None] = None

    @dc.dataclass(frozen=True)
    class Output(IoPipelineMessages.NeverInbound):
        msg: ta.Union[
            IoPipelineHttpResponseObject,
            IoPipelineMessages.FinalInput,
            'IoPipelineHttpClientMessages.Close',
        ]

        request: ta.Optional['IoPipelineHttpClientMessages.Request'] = None

    @dc.dataclass(frozen=True)
    class Close(IoPipelineMessages.NeverOutbound):
        pass


#


class IoPipelineHttpClientHandler(IoPipelineHandler):
    _request: ta.Optional[IoPipelineHttpClientMessages.Request] = None

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, IoPipelineHttpClientMessages.Request):
            check.none(self._request)
            self._request = msg

            if (ag := msg.aggregate) is not None:
                rad = check.not_none(ctx.pipeline.find_single_handler_of_type(IoPipelineHttpResponseAggregatorDecoder))
                rad.handler.set_enabled(ag)

            ctx.feed_out(msg.request)

            IoPipelineFlow.maybe_flush_output(ctx)
            IoPipelineFlow.maybe_ready_for_input(ctx)

            return

        if isinstance(msg, IoPipelineHttpResponseObject):
            ctx.feed_out(IoPipelineHttpClientMessages.Output(msg, request=self._request))

            if isinstance(msg, (FullIoPipelineHttpResponse, IoPipelineHttpResponseEnd)):
                self._request = None

            return

        if isinstance(msg, (IoPipelineMessages.FinalInput, IoPipelineHttpClientMessages.Close)):
            ctx.feed_out(IoPipelineHttpClientMessages.Output(msg, request=self._request))

            self._request = None

            if isinstance(msg, IoPipelineMessages.FinalInput):
                ctx.feed_in(msg)

            ctx.feed_out(IoPipelineMessages.FinalOutput())

            return

        ctx.feed_in(msg)
