# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - just a catchall flatmap op?
"""
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
            *,
            emit: bool = False,
            drop: bool = False,
    ) -> None:
        check.arg(emit or drop)

        super().__init__()

        if isinstance(predicate, (type, tuple)):
            self._predicate = lambda msg: isinstance(msg, predicate)  # noqa
        else:
            self._predicate = check.callable(predicate)

        self._emit = emit
        self._drop = drop

    _predicate: ta.Callable[[ta.Any], bool]

    def _handle(
            self,
            ctx: ChannelPipelineHandlerContext,
            feed_next: ta.Callable[[ta.Any], None],
            msg: ta.Any,
    ) -> None:
        if self._predicate(msg):
            if self._emit:
                ctx.emit(msg)

            if not self._drop:
                feed_next(msg)


class InboundSimplePredicateChannelPipelineHandler(SimplePredicateChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(ctx, ctx.feed_in, msg)


class OutboundSimplePredicateChannelPipelineHandler(SimplePredicateChannelPipelineHandler):
    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._handle(ctx, ctx.feed_out, msg)


class DuplexSimplePredicateChannelPipelineHandler(
    InboundSimplePredicateChannelPipelineHandler,
    OutboundSimplePredicateChannelPipelineHandler,
):
    pass
