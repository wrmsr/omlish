# @omlish-lite
import dataclasses as dc
import typing as ta
import unittest

from ...core import PipelineChannel
from ..m2mdec import MessageToMessageDecoder


@dc.dataclass()
class FooMsg:
    i: int


@dc.dataclass()
class BarMsg:
    s: str


@dc.dataclass()
class BazMsg:
    o: ta.Any


class TestM2mdec(unittest.TestCase):
    def test_m2mdec(self):
        ch = PipelineChannel([
            MessageToMessageDecoder(FooMsg, lambda _, msg: (BarMsg(str(msg.i)),)),
        ], config=PipelineChannel.Config(pipeline=PipelineChannel.PipelineConfig(terminal_mode='emit')))

        ch.feed_in(FooMsg(123), BazMsg(True))
        assert ch.drain() == [
            BarMsg('123'),
            BazMsg(True),
        ]
