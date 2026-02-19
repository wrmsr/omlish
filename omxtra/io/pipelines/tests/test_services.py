# @omlish-lite
import abc
import unittest

from omlish.lite.abstract import Abstract

from ..core import PipelineChannel
from ..core import PipelineChannelService


class FooService(PipelineChannelService, Abstract):
    @abc.abstractmethod
    def frob(self) -> str:
        raise NotImplementedError


class FooServiceImpl(FooService):
    def frob(self) -> str:
        return 'foo!'


class TestServices(unittest.TestCase):
    def test_services(self):
        ch = PipelineChannel(services=[FooServiceImpl()])
        foo = ch.services[FooService]
        assert isinstance(foo, FooServiceImpl)
        assert foo.frob() == 'foo!'
