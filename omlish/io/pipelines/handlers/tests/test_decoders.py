# ruff: noqa: UP006
# @omlish-lite
import dataclasses as dc
import typing as ta
import unittest

from .....lite.check import check
from ...core import IoPipeline
from ...core import IoPipelineHandlerContext
from ...flow.types import IoPipelineFlow
from ...flow.types import IoPipelineFlowMessages
from ...handlers.fns import IoPipelineHandlerFns
from ...handlers.queues import InboundQueueIoPipelineHandler
from ..decoders import FnMessageToMessageDecoderIoPipelineHandler
from ..decoders import MessageToMessageDecoderIoPipelineHandler


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


SIMPLE_FOO_TO_BAR_DECODER = FnMessageToMessageDecoderIoPipelineHandler(
    IoPipelineHandlerFns.isinstance(FooMsg),
    lambda _, msg: (BarMsg(str(msg.i)),),
)


##


class DuplicatingFooToBarDecoder(MessageToMessageDecoderIoPipelineHandler):
    def __init__(self, n: int = 2) -> None:
        super().__init__()

        self._n = n

    def _should_decode(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
        return isinstance(msg, FooMsg)

    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            msg: ta.Any,
            out: ta.List[ta.Any],
    ) -> None:
        for _ in range(self._n):
            out.append(BarMsg(str(msg.i)))


class AccumulatingFooToBarDecoder(MessageToMessageDecoderIoPipelineHandler):
    def __init__(self, n: int = 2) -> None:
        super().__init__()

        self._n = n

        self._lst: ta.List[FooMsg] = []

    def _should_decode(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> bool:
        return isinstance(msg, FooMsg)

    def _decode(
            self,
            ctx: IoPipelineHandlerContext,
            msg: ta.Any,
            out: ta.List[ta.Any],
    ) -> None:
        check.state(len(self._lst) < self._n)
        self._lst.append(msg)
        if len(self._lst) < self._n:
            return
        bar = BarMsg(''.join(str(x.i) for x in self._lst))
        self._lst.clear()
        out.append(bar)


##


class TestM2mdecNoFlow(unittest.TestCase):
    def test_simple(self):
        ch = IoPipeline.new([
            SIMPLE_FOO_TO_BAR_DECODER,
            ibq := InboundQueueIoPipelineHandler(),
        ])

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ibq.drain() == [
            BarMsg('123'),
            BazMsg(True),
        ]

    def test_duplicating(self):
        ch = IoPipeline.new([
            DuplicatingFooToBarDecoder(),
            ibq := InboundQueueIoPipelineHandler(),
        ])

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ibq.drain() == [
            BarMsg('123'),
            BarMsg('123'),
            BazMsg(True),
        ]

    def test_accumulating(self):
        ch = IoPipeline.new([
            AccumulatingFooToBarDecoder(),
            ibq := InboundQueueIoPipelineHandler(),
        ])

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ibq.drain() == [
            BazMsg(True),
        ]

        ch.feed_in(BazMsg(420))
        assert ibq.drain() == [
            BazMsg(420),
        ]

        ch.feed_in(FooMsg(420), BazMsg(421))
        assert ibq.drain() == [
            BarMsg('123420'),
            BazMsg(421),
        ]


class MyFlow(IoPipelineFlow):
    def __init__(self, *, auto_read: bool) -> None:
        super().__init__()

        self._auto_read = auto_read

    def is_auto_read(self) -> bool:
        return self._auto_read

    def set_auto_read(self, auto_read: bool) -> None:
        self._auto_read = auto_read


class TestM2mdecMyFlow(unittest.TestCase):
    def test_m2mdec(self):
        ch = IoPipeline.new(
            [
                SIMPLE_FOO_TO_BAR_DECODER,
                ibq := InboundQueueIoPipelineHandler(),
            ],
            services=[mf := MyFlow(auto_read=True)],  # noqa
        )

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ibq.drain() == [
            BarMsg('123'),
            BazMsg(True),
        ]

    def test_duplicating(self):
        ch = IoPipeline.new(
            [
                DuplicatingFooToBarDecoder(),
                ibq := InboundQueueIoPipelineHandler(),
            ],
            services=[mf := MyFlow(auto_read=True)],  # noqa
        )

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ibq.drain() == [
            BarMsg('123'),
            BarMsg('123'),
            BazMsg(True),
        ]

    def test_accumulating_auto_read(self):
        ch = IoPipeline.new(
            [
                AccumulatingFooToBarDecoder(),
                ibq := InboundQueueIoPipelineHandler(),
            ],
            services=[mf := MyFlow(auto_read=True)],  # noqa
        )

        #

        ch.feed_in(FooMsg(123), BazMsg(True), IoPipelineFlowMessages.FlushInput())
        assert ibq.drain() == [
            BazMsg(True),
            IoPipelineFlowMessages.FlushInput(),
        ]

        ch.feed_in(BazMsg(420), IoPipelineFlowMessages.FlushInput())
        assert ibq.drain() == [
            BazMsg(420),
            IoPipelineFlowMessages.FlushInput(),
        ]

        ch.feed_in(IoPipelineFlowMessages.FlushInput())
        assert ibq.drain() == [IoPipelineFlowMessages.FlushInput()]

        ch.feed_in(FooMsg(420), BazMsg(421), IoPipelineFlowMessages.FlushInput())
        assert ibq.drain() == [
            BarMsg('123420'),
            BazMsg(421),
            IoPipelineFlowMessages.FlushInput(),
        ]

        ch.feed_in(FooMsg(123), IoPipelineFlowMessages.FlushInput())
        assert ibq.drain() == [
            IoPipelineFlowMessages.FlushInput(),
        ]

        ch.feed_in(FooMsg(123), IoPipelineFlowMessages.FlushInput())
        assert ibq.drain() == [
            BarMsg('123123'),
            IoPipelineFlowMessages.FlushInput(),
        ]

    def test_accumulating_no_auto_read(self):
        ch = IoPipeline.new(
            [
                AccumulatingFooToBarDecoder(),
                ibq := InboundQueueIoPipelineHandler(),
            ],
            services=[mf := MyFlow(auto_read=False)],  # noqa
        )

        #

        ch.feed_in(FooMsg(123), BazMsg(True), IoPipelineFlowMessages.FlushInput())
        assert ch.output.drain() == [IoPipelineFlowMessages.ReadyForInput()]
        assert ibq.drain() == [
            BazMsg(True),
            IoPipelineFlowMessages.FlushInput(),
        ]

        ch.feed_in(BazMsg(420), IoPipelineFlowMessages.FlushInput())
        assert ch.output.drain() == []
        assert ibq.drain() == [
            BazMsg(420),
            IoPipelineFlowMessages.FlushInput(),
        ]

        ch.feed_in(IoPipelineFlowMessages.FlushInput())
        assert ch.output.drain() == []
        assert ibq.drain() == [IoPipelineFlowMessages.FlushInput()]

        ch.feed_in(FooMsg(420), BazMsg(421), IoPipelineFlowMessages.FlushInput())
        assert ch.output.drain() == []
        assert ibq.drain() == [
            BarMsg('123420'),
            BazMsg(421),
            IoPipelineFlowMessages.FlushInput(),
        ]

        #

        ch.feed_in(FooMsg(123), IoPipelineFlowMessages.FlushInput())
        assert ch.output.drain() == [IoPipelineFlowMessages.ReadyForInput()]
        assert ibq.drain() == [IoPipelineFlowMessages.FlushInput()]

        ch.feed_in(FooMsg(123), IoPipelineFlowMessages.FlushInput())
        assert ch.output.drain() == []
        assert ibq.drain() == [
            BarMsg('123123'),
            IoPipelineFlowMessages.FlushInput(),
        ]
