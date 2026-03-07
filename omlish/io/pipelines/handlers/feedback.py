# ruff: noqa: UP006 UP037 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext


##


class FeedbackInboundChannelPipelineHandler(ChannelPipelineHandler):
    @ta.final
    @dc.dataclass(frozen=True)
    class FeedbackMessages:
        msgs: ta.Iterable[ta.Any]

        _handler: ta.Optional['FeedbackInboundChannelPipelineHandler'] = None

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not isinstance(msg, FeedbackInboundChannelPipelineHandler.FeedbackMessages):
            ctx.feed_in(msg)
            return

        if not (msg._handler is None or msg._handler is self):  # noqa
            ctx.feed_in(msg)
            return

        for m in msg.msgs:
            ctx.feed_out(m)

    def wrap(self, *msgs: ta.Any) -> FeedbackMessages:
        return FeedbackInboundChannelPipelineHandler.FeedbackMessages(msgs, self)
