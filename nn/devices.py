import abc
import operator
import typing as ta

from omlish import check
from omlish import lang
import numpy as np

from .ops import BinaryOp
from .ops import MovementOp
from .ops import ReduceOp
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


class CpuDevice(Device):
    @property
    def evaluator(self) -> 'evaluators.Evaluator':
        return numpy_interpreter()


DEFAULT_DEVICE: Device = CpuDevice()


def shape_to_axis(old_shape: ta.Sequence[int], new_shape: ta.Sequence[int]) -> ta.Sequence[int]:
    check.arg(len(old_shape) == len(new_shape), 'reduce shapes must have same dimensions')
    return tuple(i for i, (a, b) in enumerate(zip(old_shape, new_shape)) if a != b)


@lang.cached_nullary
def numpy_interpreter() -> 'evaluators.Interpreter':
    return evaluators.Interpreter(
        RawCpuBuffer,
        {
            BinaryOp.ADD: operator.add,
            BinaryOp.MUL: operator.mul,

            ReduceOp.SUM: lambda x, new_shape: (
                x.sum(shape_to_axis(x.shape, new_shape), keepdims=True)
                if tuple(x.shape) != tuple(new_shape) else x[:]
            ),

            MovementOp.EXPAND: np.broadcast_to,
        },
    )
