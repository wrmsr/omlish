# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check

from .core import ChannelPipelineHandler
from .core import ChannelPipelineHandlerContext


##


class SimplePredicateChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    def __init__(
            self,
            predicate: ta.Union[type, ta.Tuple[type, ...], ta.Callable[[ta.Any], bool]],
    ) -> None:
        super().__init__()

        if isinstance(predicate, (type, tuple)):
            self._predicate = lambda msg: isinstance(msg, predicate)  # noqa
        else:
            self._predicate = check.callable(predicate)

    _predicate: ta.Callable[[ta.Any], bool]


##


class DroppingChannelPipelineHandler(SimplePredicateChannelPipelineHandler, Abstract):
    pass


class InboundDroppingChannelPipelineHandler(DroppingChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not self._predicate(msg):
            ctx.feed_in(msg)


class OutboundDroppingChannelPipelineHandler(DroppingChannelPipelineHandler):
    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if not self._predicate(msg):
            ctx.feed_out(msg)


class DuplexDroppingChannelPipelineHandler(
    InboundDroppingChannelPipelineHandler,
    OutboundDroppingChannelPipelineHandler,
):
    pass


##


class EmittingChannelPipelineHandler(SimplePredicateChannelPipelineHandler, Abstract):
    pass


class InboundEmittingChannelPipelineHandler(EmittingChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._predicate(msg):
            ctx.emit(msg)

        ctx.feed_in(msg)


class OutboundEmittingChannelPipelineHandler(EmittingChannelPipelineHandler):
    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if self._predicate(msg):
            ctx.emit(msg)

        ctx.feed_out(msg)


class DuplexEmittingChannelPipelineHandler(
    InboundEmittingChannelPipelineHandler,
    OutboundEmittingChannelPipelineHandler,
):
    pass
