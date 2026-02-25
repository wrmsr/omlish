# @omlish-lite
import abc
import unittest

from omlish.lite.abstract import Abstract

from ..core import ChannelPipelineService
from ..core import PipelineChannel


class FooService(ChannelPipelineService, Abstract):
    @abc.abstractmethod
    def frob(self) -> str:
        raise NotImplementedError


class FooServiceImpl(FooService):
    def frob(self) -> str:
        return 'foo!'


class TestServices(unittest.TestCase):
    def test_services(self):
        ch = PipelineChannel.new(services=[FooServiceImpl()])
        foo = ch.services[FooService]
        assert isinstance(foo, FooServiceImpl)
        assert foo.frob() == 'foo!'
