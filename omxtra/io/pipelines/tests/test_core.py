# @omlish-lite
import typing as ta
import unittest

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import PipelineChannel


class IntIncInboundHandler(ChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, int):
            msg += 1

        ctx.feed_in(msg)


class IntMulThreeInboundHandler(ChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, int):
            msg *= 3

        ctx.feed_in(msg)


class IntStrDuplexHandler(ChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, int):
            msg = str(msg)

        ctx.feed_in(msg)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        if isinstance(msg, str):
            msg = int(msg)

        ctx.feed_out(msg)


class DuplicateInboundHandler(ChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        ctx.feed_in(msg)
        ctx.feed_in(msg)


class ReplaceSelfInboundHandler(ChannelPipelineHandler):
    def __init__(self, fn):
        self.fn = fn

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        h = self.fn()
        ctx.pipeline.replace(self, h)
        ctx.pipeline.feed_in_to(h, msg)


class TestCore(unittest.TestCase):
    def test_core(self):
        ch = PipelineChannel([
            IntIncInboundHandler(),
            IntStrDuplexHandler(),
        ])

        ch.feed_in('hi')
        assert ch.drain() == ['hi']

        ch.feed_in(42)
        assert ch.drain() == ['43']

        ch.feed_out('24')
        assert ch.drain() == [24]

        #

        ch.pipeline.add_outermost(
            IntMulThreeInboundHandler(),
        )

        ch.feed_in(42)
        assert ch.drain() == ['127']

        ch.feed_out('24')
        assert ch.drain() == [24]

        #

        ch.pipeline.remove(ch.pipeline.handlers()[1])

        ch.feed_in(42)
        assert ch.drain() == ['126']

        ch.feed_out(24)
        assert ch.drain() == [24]

        #

        ch.pipeline.replace(ch.pipeline.handlers()[0], IntIncInboundHandler())

        ch.feed_in('hi')
        assert ch.drain() == ['hi']

        ch.feed_in(42)
        assert ch.drain() == ['43']

        ch.feed_out('24')
        assert ch.drain() == [24]

    def test_replace_self(self):
        ch = PipelineChannel([
            DuplicateInboundHandler(),
            ReplaceSelfInboundHandler(IntIncInboundHandler),
            IntStrDuplexHandler(),
        ])

        ch.feed_in(42)
        assert ch.drain() == ['43', '43']
