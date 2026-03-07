# @omlish-lite
import abc
import unittest

from ....lite.abstract import Abstract
from ..core import IoPipeline
from ..core import IoPipelineService


class FooService(IoPipelineService, Abstract):
    @abc.abstractmethod
    def frob(self) -> str:
        raise NotImplementedError


class FooServiceImpl(FooService):
    def frob(self) -> str:
        return 'foo!'


class TestServices(unittest.TestCase):
    def test_services(self):
        ch = IoPipeline.new(services=[FooServiceImpl()])
        foo = ch.services[FooService]
        assert isinstance(foo, FooServiceImpl)
        assert foo.frob() == 'foo!'
