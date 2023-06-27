import abc
import operator
import typing as ta

from omlish import check
from omlish import lang
import numpy as np

from .ops import BinaryOp
from .ops import MovementOp
from .ops import ReduceOp
from .ops import UnaryOp
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
        return numpy_interpreter()

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


def shape_to_axis(old_shape: ta.Sequence[int], new_shape: ta.Sequence[int]) -> ta.Sequence[int]:
    check.arg(len(old_shape) == len(new_shape), 'reduce shapes must have same dimensions')
    return tuple(i for i, (a, b) in enumerate(zip(old_shape, new_shape)) if a != b)


@lang.cached_nullary
def numpy_interpreter() -> 'evaluators.Interpreter':
    return evaluators.Interpreter(
        RawCpuBuffer,
        {
            BinaryOp.ADD: operator.add,
            BinaryOp.SUB: operator.sub,
            BinaryOp.MUL: operator.mul,
            BinaryOp.DIV: operator.truediv,

            ReduceOp.SUM: lambda x, new_shape: (
                x.sum(shape_to_axis(x.shape, new_shape), keepdims=True)
                if tuple(x.shape) != tuple(new_shape) else x[:]
            ),

            ReduceOp.MAX: lambda x, new_shape: (
                (x.amax if hasattr(x, 'amax') else x.max)(shape_to_axis(x.shape, new_shape), keepdims=True)
                if tuple(x.shape) != tuple(new_shape) else x[:]
            ),

            BinaryOp.MAX: np.maximum,
            BinaryOp.CMP_EQ: lambda x, y: (x == y).astype(np.float32),  # noqa

            UnaryOp.EXP2: np.exp2,
            UnaryOp.LOG2: np.log2,

            MovementOp.EXPAND: np.broadcast_to,
            MovementOp.RESHAPE: lambda x, arg: x.reshape(arg),
            MovementOp.PERMUTE: lambda x, order: x.transpose(order),
            MovementOp.PAD: np.pad,
        },
    )
