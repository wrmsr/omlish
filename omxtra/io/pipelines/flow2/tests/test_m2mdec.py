# ruff: noqa: UP006
# @omlish-lite
import dataclasses as dc
import typing as ta
import unittest

from omlish.lite.check import check

from ...core import ChannelPipelineHandlerContext
from ...core import PipelineChannel
from ...handlers.fns import ChannelPipelineHandlerFns
from ..m2mdec import FnMessageToMessageDecoder
from ..m2mdec import MessageToMessageDecoder
from ..types import PipelineChannelFlow
from ..types import PipelineChannelFlowMessages


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


SIMPLE_FOO_TO_BAR_DECODER = FnMessageToMessageDecoder(
    ChannelPipelineHandlerFns.isinstance(FooMsg),
    lambda _, msg: (BarMsg(str(msg.i)),),
)


EMIT_TERMINAL_CHANNEL_CONFIG = PipelineChannel.Config(
    pipeline=PipelineChannel.PipelineConfig(
        terminal_mode='emit',
    ),
)


##


class DuplicatingFooToBarDecoder(MessageToMessageDecoder):
    def __init__(self, n: int = 2) -> None:
        super().__init__()

        self._n = n

    def _should_decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
        return isinstance(msg, FooMsg)

    def _decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
        return [BarMsg(str(msg.i))] * self._n


class AccumulatingFooToBarDecoder(MessageToMessageDecoder):
    def __init__(self, n: int = 2) -> None:
        super().__init__()

        self._n = n

        self._lst: ta.List[FooMsg] = []

    def _should_decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
        return isinstance(msg, FooMsg)

    def _decode(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
        check.state(len(self._lst) < self._n)
        self._lst.append(msg)
        if len(self._lst) < self._n:
            return ()
        bar = BarMsg(''.join(str(x.i) for x in self._lst))
        self._lst.clear()
        return (bar,)


##


class TestM2mdecNoFlow(unittest.TestCase):
    def test_simple(self):
        ch = PipelineChannel(
            [SIMPLE_FOO_TO_BAR_DECODER],
            config=EMIT_TERMINAL_CHANNEL_CONFIG,
        )

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ch.drain() == [
            BarMsg('123'),
            BazMsg(True),
        ]

    def test_duplicating(self):
        ch = PipelineChannel(
            [DuplicatingFooToBarDecoder()],
            config=EMIT_TERMINAL_CHANNEL_CONFIG,
        )

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ch.drain() == [
            BarMsg('123'),
            BarMsg('123'),
            BazMsg(True),
        ]

    def test_accumulating(self):
        ch = PipelineChannel(
            [AccumulatingFooToBarDecoder()],
            config=EMIT_TERMINAL_CHANNEL_CONFIG,
        )

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ch.drain() == [
            BazMsg(True),
        ]

        ch.feed_in(BazMsg(420))
        assert ch.drain() == [
            BazMsg(420),
        ]

        ch.feed_in(FooMsg(420), BazMsg(421))
        assert ch.drain() == [
            BarMsg('123420'),
            BazMsg(421),
        ]


class MyFlow(PipelineChannelFlow):
    def __init__(self, *, auto_read: bool) -> None:
        super().__init__()

        self._auto_read = auto_read

    @property
    def is_auto_read(self) -> bool:
        return self._auto_read

    def set_auto_read(self, auto_read: bool) -> None:
        self._auto_read = auto_read


class TestM2mdecMyFlow(unittest.TestCase):
    def test_m2mdec(self):
        ch = PipelineChannel(
            [
                SIMPLE_FOO_TO_BAR_DECODER,
            ],
            config=EMIT_TERMINAL_CHANNEL_CONFIG,
            services=[mf := MyFlow(auto_read=True)],  # noqa
        )

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ch.drain() == [
            BarMsg('123'),
            BazMsg(True),
        ]

    def test_duplicating(self):
        ch = PipelineChannel(
            [DuplicatingFooToBarDecoder()],
            config=EMIT_TERMINAL_CHANNEL_CONFIG,
            services=[mf := MyFlow(auto_read=True)],  # noqa
        )

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ch.drain() == [
            BarMsg('123'),
            BarMsg('123'),
            BazMsg(True),
        ]

    def test_accumulating_auto_read(self):
        ch = PipelineChannel(
            [AccumulatingFooToBarDecoder()],
            config=EMIT_TERMINAL_CHANNEL_CONFIG,
            services=[mf := MyFlow(auto_read=True)],  # noqa
        )

        #

        ch.feed_in(FooMsg(123), BazMsg(True), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            BazMsg(True),
            PipelineChannelFlowMessages.FlushInput(),
        ]

        ch.feed_in(BazMsg(420), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            BazMsg(420),
            PipelineChannelFlowMessages.FlushInput(),
        ]

        ch.feed_in(PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [PipelineChannelFlowMessages.FlushInput()]

        ch.feed_in(FooMsg(420), BazMsg(421), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            BarMsg('123420'),
            BazMsg(421),
            PipelineChannelFlowMessages.FlushInput(),
        ]

        ch.feed_in(FooMsg(123), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            PipelineChannelFlowMessages.FlushInput(),
        ]

        ch.feed_in(FooMsg(123), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            BarMsg('123123'),
            PipelineChannelFlowMessages.FlushInput(),
        ]

    def test_accumulating_no_auto_read(self):
        ch = PipelineChannel(
            [AccumulatingFooToBarDecoder()],
            config=EMIT_TERMINAL_CHANNEL_CONFIG,
            services=[mf := MyFlow(auto_read=False)],  # noqa
        )

        #

        ch.feed_in(FooMsg(123), BazMsg(True), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            BazMsg(True),
            PipelineChannelFlowMessages.FlushInput(),
        ]

        ch.feed_in(BazMsg(420), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            BazMsg(420),
            PipelineChannelFlowMessages.FlushInput(),
        ]

        ch.feed_in(PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [PipelineChannelFlowMessages.FlushInput()]

        ch.feed_in(FooMsg(420), BazMsg(421), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            BarMsg('123420'),
            BazMsg(421),
            PipelineChannelFlowMessages.FlushInput(),
        ]

        #

        ch.feed_in(FooMsg(123), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            PipelineChannelFlowMessages.ReadyForInput(),
            PipelineChannelFlowMessages.FlushInput(),
        ]

        ch.feed_in(FooMsg(123), PipelineChannelFlowMessages.FlushInput())
        assert ch.drain() == [
            BarMsg('123123'),
            PipelineChannelFlowMessages.FlushInput(),
        ]
