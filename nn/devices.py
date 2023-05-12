import abc
import typing as ta

from omlish import lang

from .raw import RawCpuBuffer

if ta.TYPE_CHECKING:
    from . import eval as eval_
else:
    eval = lang.proxy_import('.eval', __package__)


class Device(lang.Abstract):
    @property
    @abc.abstractmethod
    def evaluator(self) -> 'eval_.Evaluator':
        raise NotImplementedError


class CpuDevice(Device):
    @property
    def evaluator(self) -> 'eval_.Evaluator':
        return numpy_interpreter()


DEFAULT_DEVICE: Device = CpuDevice()


@lang.cached_nullary
def numpy_interpreter() -> 'eval_.Interpreter':
    return eval_.Interpreter(
        RawCpuBuffer,
        {},
    )
