# @omlish-lite
import typing as ta
import unittest

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import PipelineChannel
from ..handlers.queues import InboundQueueChannelPipelineHandler


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
        hr = ctx.pipeline.replace(ctx.ref, h)
        ctx.channel.feed_in_to(hr, msg)


class TestCore(unittest.TestCase):
    def test_core(self):
        ch = PipelineChannel([
            IntIncInboundHandler(),
            IntStrDuplexHandler(),
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        ch.feed_in('hi')
        assert ibq.drain() == ['hi']

        ch.feed_in(42)
        assert ibq.drain() == ['43']

        ch.pipeline._innermost.feed_out('24')  # noqa
        assert ch.drain() == [24]

        #

        ch.pipeline.add_outer_to(
            ch.pipeline.handlers()[0],
            IntMulThreeInboundHandler(),
        )

        ch.feed_in(42)
        assert ibq.drain() == ['127']

        ch.pipeline._innermost.feed_out('24')  # noqa
        assert ch.drain() == [24]

        #

        ch.pipeline.remove(ch.pipeline.handlers()[1])

        ch.feed_in(42)
        assert ibq.drain() == ['126']

        ch.pipeline._innermost.feed_out('24')  # noqa
        assert ch.drain() == [24]

        #

        ch.pipeline.replace(ch.pipeline.handlers()[0], IntIncInboundHandler())

        ch.feed_in('hi')
        assert ibq.drain() == ['hi']

        ch.feed_in(42)
        assert ibq.drain() == ['43']

        ch.pipeline._innermost.feed_out('24')  # noqa
        assert ch.drain() == [24]

    def test_replace_self(self):
        ch = PipelineChannel([
            DuplicateInboundHandler(),
            ReplaceSelfInboundHandler(IntIncInboundHandler),
            IntStrDuplexHandler(),
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        ch.feed_in(42)
        assert ibq.drain() == ['43', '43']

    def test_named(self):
        ch = PipelineChannel([
            ibq := InboundQueueChannelPipelineHandler(),
        ])

        ch.pipeline.add_outermost(IntStrDuplexHandler(), name='int_str')
        ch.pipeline.add_outer_to(ch.pipeline.handlers()[0], IntIncInboundHandler(), name='int_inc')

        ch.feed_in(42)
        assert ibq.drain() == ['43']

        ch.pipeline._innermost.feed_out('24')  # noqa
        assert ch.drain() == [24]

        ch.pipeline.remove(ch.pipeline.handlers_by_name()['int_inc'])

        ch.feed_in(42)
        assert ibq.drain() == ['42']

        ch.pipeline._innermost.feed_out('24')  # noqa
        assert ch.drain() == [24]
