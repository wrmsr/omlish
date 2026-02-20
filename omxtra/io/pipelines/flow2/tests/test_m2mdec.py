# @omlish-lite
import dataclasses as dc
import typing as ta
import unittest

from ...core import ChannelPipelineHandlerContext
from ...core import PipelineChannel
from ...handlers.fns import ChannelPipelineHandlerFns
from ..m2mdec import FnMessageToMessageDecoder
from ..m2mdec import MessageToMessageDecoder
from ..types import PipelineChannelFlow


##


@dc.dataclass()
class FooMsg:
    i: int


@dc.dataclass()
class BarMsg:
    s: str


@dc.dataclass()
class BazMsg:
    o: ta.Any


FOO_TO_BAR_DECODER = FnMessageToMessageDecoder(
    ChannelPipelineHandlerFns.isinstance(FooMsg),
    lambda _, msg: (BarMsg(str(msg.i)),),
)


EMIT_TERMINAL_CHANNEL_CONFIG = PipelineChannel.Config(
    pipeline=PipelineChannel.PipelineConfig(
        terminal_mode='emit',
    ),
)


##


class TestM2mdecNoFlow(unittest.TestCase):
    def test_m2mdec(self):
        ch = PipelineChannel(
            [
                FOO_TO_BAR_DECODER,
            ],
            config=EMIT_TERMINAL_CHANNEL_CONFIG,
        )

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ch.drain() == [
            BarMsg('123'),
            BazMsg(True),
        ]


##


class DoublingFooToBarDecoder(MessageToMessageDecoder):
    def _should_decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
        return isinstance(msg, FooMsg)

    def _decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
        return [
            BarMsg(str(msg.i)),
            BarMsg(str(msg.i)),
        ]


class MyFlow(PipelineChannelFlow):
    @property
    def is_auto_read(self) -> bool:
        return True


class TestM2mdecMyFlow(unittest.TestCase):
    def test_m2mdec(self):
        ch = PipelineChannel(
            [
                FOO_TO_BAR_DECODER,
            ],
            config=EMIT_TERMINAL_CHANNEL_CONFIG,
            services=[mf := MyFlow()],  # noqa
        )

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ch.drain() == [
            BarMsg('123'),
            BazMsg(True),
        ]
