import typing as ta

from omlish import lang

if ta.TYPE_CHECKING:
    import pyopencl as cl
else:
    cl = lang.proxy_import('pyopencl')

from .devices import Device
from .evaluators import Evaluator


class OpenclDevice(Device):
    @property
    def evaluator(self) -> Evaluator:
        raise NotImplementedError
