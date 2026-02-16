# @omlish-lite
import typing as ta
import unittest

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import PipelineChannel


class TestCore(unittest.TestCase):
    def test_core(self):
        class IntIncInboundHandler(ChannelPipelineHandler):
            def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
                if isinstance(msg, int):
                    msg += 1

                ctx.feed_in(msg)

        class IntStrDuplexHandler(ChannelPipelineHandler):
            def inbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
                if isinstance(msg, int):
                    msg = str(msg)

                ctx.feed_in(msg)

            def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
                if isinstance(msg, str):
                    msg = int(msg)

                ctx.feed_out(msg)

        #

        ch = PipelineChannel([
            IntIncInboundHandler(),
            IntStrDuplexHandler(),
        ])

        ch.feed_in(420)
        assert ch.drain_out() == ['421']

        ch.feed_out('240')
        assert ch.drain_out() == [240]

        #

        ch.pipeline.add_outermost(
            IntIncInboundHandler(),
        )

        ch.feed_in(420)
        assert ch.drain_out() == ['422']

        ch.feed_out('240')
        assert ch.drain_out() == [240]

        #

        ch.pipeline.remove(ch.pipeline.handlers()[-1])

        ch.feed_in(420)
        assert ch.drain_out() == [422]

        ch.feed_out(240)
        assert ch.drain_out() == [240]
