import abc
import operator
import typing as ta

from omlish import check
from omlish import lang
import numpy as np

from . import ops
from .raw import RawBuffer
from .raw import RawCpuBuffer

if ta.TYPE_CHECKING:
    from . import evaluators
else:
    evaluators = lang.proxy_import('.evaluators', __package__)


class Device(lang.Abstract):
    @property
    @abc.abstractmethod
    def evaluator(self) -> 'evaluators.Evaluator':
        raise NotImplementedError

    @abc.abstractmethod
    def make_raw_buffer(self, obj: ta.Any) -> RawBuffer:
        raise NotImplementedError


class CpuDevice(Device):
    @property
    def evaluator(self) -> 'evaluators.Evaluator':
        from . evaluators import NumpyInterpreter
        return NumpyInterpreter()

    def make_raw_buffer(self, obj: ta.Any) -> RawCpuBuffer:
        return RawCpuBuffer.from_cpu(obj)  # noqa


@lang.cached_nullary
def cpu_device() -> CpuDevice:
    return CpuDevice()


@lang.cached_nullary
def default_device() -> Device:
    from .opencl import OpenclDevice
    return OpenclDevice()
    # return cpu_device()
