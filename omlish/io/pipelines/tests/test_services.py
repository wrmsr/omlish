# @omlish-lite
import abc
import unittest

from ....lite.abstract import Abstract
from ..core import ChannelPipeline
from ..core import ChannelPipelineService


class FooService(ChannelPipelineService, Abstract):
    @abc.abstractmethod
    def frob(self) -> str:
        raise NotImplementedError


class FooServiceImpl(FooService):
    def frob(self) -> str:
        return 'foo!'


class TestServices(unittest.TestCase):
    def test_services(self):
        ch = ChannelPipeline.new(services=[FooServiceImpl()])
        foo = ch.services[FooService]
        assert isinstance(foo, FooServiceImpl)
        assert foo.frob() == 'foo!'
