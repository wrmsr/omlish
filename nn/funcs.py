import abc
import typing as ta

from omlish import check
from omlish import lang

from .dims import Shape
from .devices import Device
from .lazy import LazyBuffer
from .ops import BinaryOp
from .ops import ReduceOp
from .ops import MovementOp


if ta.TYPE_CHECKING:
    from . import tensors as tn
else:
    tn = lang.proxy_import('.tensor', __package__)


class Func(lang.Abstract):

    def __init__(self, device: Device, *parents: 'tn.Tensor') -> None:
        super().__init__()

        self._device = check.isinstance(device, Device)
        self._parents = tuple(check.isinstance(p, tn.Tensor) for p in parents)

        self._needs_input_grad = tuple(t.requires_grad for t in parents)

        self._requires_grad: ta.Optional[bool] = None
        if any(self._needs_input_grad):
            self._requires_grad = True
        elif not any(x is None for x in self._needs_input_grad):
            self._requires_grad = False

    @property
    def device(self) -> Device:
        return self._device

    @property
    def parents(self) -> ta.Sequence['tn.Tensor']:
        return self._parents

    @property
    def needs_input_grad(self) -> ta.Sequence[ta.Optional[bool]]:
        return self._needs_input_grad

    @property
    def requires_grad(self) -> ta.Optional[bool]:
        return self._requires_grad

    @abc.abstractmethod
    def forward(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def backward(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def apply(cls: ta.Type['Func'], *args: 'tn.Tensor', **kwargs: ta.Any) -> 'tn.Tensor':
        func = cls(args[0].device, *args)
        ret = tn.Tensor.of(
            func.forward(*[t.data for t in args], **kwargs),
            device=func.device,
            requires_grad=func.requires_grad,
            func=func,
        )
        return ret


class Mul(Func):
    _x: LazyBuffer
    _y: LazyBuffer

    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        self._x, self._y = x, y
        return x.binary_op(BinaryOp.MUL, y)

    def backward(self, grad_output: LazyBuffer) -> ta.Tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            self._y.binary_op(BinaryOp.MUL, grad_output) if self._needs_input_grad[0] else None,
            self._x.binary_op(BinaryOp.MUL, grad_output) if self._needs_input_grad[1] else None,
        )


class Expand(Func):
    _input_shape: Shape

    def forward(self, x: LazyBuffer, shape: ShapeType) -> LazyBuffer:
        self._input_shape = x.shape
        return x.movement_op(MovementOp.EXPAND, shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.reduce_op(ReduceOp.SUM, self._input_shape)


class Reshape(Func):
    _input_shape: Shape

    def forward(self, x: LazyBuffer, shape: ShapeType) -> LazyBuffer:
        self._input_shape = x.shape
        return x.movement_op(MovementOp.RESHAPE, shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.movement_op(MovementOp.RESHAPE, self._input_shape)

