# @omlish-lite
import typing as ta
import unittest

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import PipelineChannel


class TestCore(unittest.TestCase):
    def test_core(self):
        class IntIncHandler(ChannelPipelineHandler):
            def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
                if isinstance(msg, int):
                    msg += 1

                ctx.feed_in(msg)

        class IntStrHandler(ChannelPipelineHandler):
            def inbound(self, ctx: 'ChannelPipelineHandlerContext', msg: ta.Any) -> None:
                if isinstance(msg, int):
                    msg = str(msg)

                ctx.feed_in(msg)

        ch = PipelineChannel([
            IntIncHandler(),
            IntStrHandler(),
        ])

        ch.feed_in(420)
        assert ch.drain_out() == ['421']
