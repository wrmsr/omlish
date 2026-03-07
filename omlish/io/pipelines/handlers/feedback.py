# ruff: noqa: UP006 UP037 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ..core import IoPipelineHandler
from ..core import IoPipelineHandlerContext


##


class FeedbackInboundIoPipelineHandler(IoPipelineHandler):
    @ta.final
    @dc.dataclass(frozen=True)
    class FeedbackMessages:
        msgs: ta.Iterable[ta.Any]

        _handler: ta.Optional['FeedbackInboundIoPipelineHandler'] = None

    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, FeedbackInboundIoPipelineHandler.FeedbackMessages):
            ctx.feed_in(msg)
            return

        if not (msg._handler is None or msg._handler is self):  # noqa
            ctx.feed_in(msg)
            return

        for m in msg.msgs:
            ctx.feed_out(m)

    def wrap(self, *msgs: ta.Any) -> FeedbackMessages:
        return FeedbackInboundIoPipelineHandler.FeedbackMessages(msgs, self)
