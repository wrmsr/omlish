import abc
import math
import typing as ta

from omlish import check
from omlish import lang

from .devices import Device
from .dims import Shape
from .lazy import LazyBuffer
from .ops import BinaryOp
from .ops import MovementOp
from .ops import ReduceOp
from .ops import UnaryOp


if ta.TYPE_CHECKING:
    from . import tensor
else:
    tensor = lang.proxy_import('.tensor', __package__)


class Func(lang.Abstract):

    def __init__(self, device: Device, *parents: 'tensor.Tensor') -> None:
        super().__init__()

        self._device = check.isinstance(device, Device)
        self._parents = tuple(check.isinstance(p, tensor.Tensor) for p in parents)

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
    def parents(self) -> ta.Sequence['tensor.Tensor']:
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
    def apply(cls: ta.Type['Func'], *args: 'tensor.Tensor', **kwargs: ta.Any) -> 'tensor.Tensor':
        func = cls(args[0].device, *args)
        ret = tensor.Tensor.of(
            func.forward(*[t.data for t in args], **kwargs),
            device=func.device,
            requires_grad=func.requires_grad,
            func=func,
        )
        return ret


class Add(Func):
    _x: LazyBuffer
    _y: LazyBuffer

    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        self._x = x
        self._y = y
        return x.binary_op(BinaryOp.ADD, y)

    def backward(self, grad_output: LazyBuffer) -> ta.Tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            grad_output if self._needs_input_grad[0] else None,
            grad_output if self._needs_input_grad[1] else None,
        )


class Sub(Func):

    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        return x.binary_op(BinaryOp.SUB, y)

    def backward(self, grad_output: LazyBuffer) -> ta.Tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            grad_output if self.needs_input_grad[0] else None,
            grad_output.const_like(0).binary_op(BinaryOp.SUB, grad_output) if self.needs_input_grad[1] else None,
        )


class Mul(Func):
    _x: LazyBuffer
    _y: LazyBuffer

    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        self._x = x
        self._y = y
        return x.binary_op(BinaryOp.MUL, y)

    def backward(self, grad_output: LazyBuffer) -> ta.Tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            self._y.binary_op(BinaryOp.MUL, grad_output) if self._needs_input_grad[0] else None,
            self._x.binary_op(BinaryOp.MUL, grad_output) if self._needs_input_grad[1] else None,
        )


class Div(Func):
    _x: LazyBuffer
    _y: LazyBuffer

    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        self._x = x
        self._y = y
        return x.binary_op(BinaryOp.DIV, y)

    def backward(self, grad_output: LazyBuffer) -> ta.Tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            grad_output.binary_op(BinaryOp.DIV, self._y) if self.needs_input_grad[0] else None,
            (
                grad_output
                .const_like(0)
                .binary_op(BinaryOp.SUB, grad_output)
                .binary_op(BinaryOp.MUL, self._x)
                .binary_op(BinaryOp.DIV, self._y.binary_op(BinaryOp.MUL, self._y))
            ) if self.needs_input_grad[1] else None
        )


class Expand(Func):
    _input_shape: Shape

    def forward(self, x: LazyBuffer, shape: Shape) -> LazyBuffer:
        self._input_shape = x.shape
        return x.movement_op(MovementOp.EXPAND, shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.reduce_op(ReduceOp.SUM, self._input_shape)


class Reshape(Func):
    _input_shape: Shape

    def forward(self, x: LazyBuffer, shape: Shape) -> LazyBuffer:
        self._input_shape = x.shape
        return x.movement_op(MovementOp.RESHAPE, shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.movement_op(MovementOp.RESHAPE, self._input_shape)


class Sum(Func):
    _input_shape: Shape

    def forward(self, x: LazyBuffer, shape: Shape) -> LazyBuffer:
        self._input_shape = x.shape
        return x.reduce_op(ReduceOp.SUM, shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.movement_op(MovementOp.EXPAND, self._input_shape)


class Contiguous(Func):

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        return x.contiguous()

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output


class Permute(Func):
    _input_order: ta.Sequence[int]

    def forward(self, x: LazyBuffer, order: ta.Sequence[int]) -> LazyBuffer:
        self._input_order = order
        return x.movement_op(MovementOp.PERMUTE, order)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        output_order = tuple(t[0] for t in sorted(enumerate(self._input_order), key=lambda t: t[1]))
        return grad_output.movement_op(MovementOp.PERMUTE, output_order)


class Relu(Func):
    _ret: LazyBuffer

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self._ret = x.binary_op(BinaryOp.MAX, x.const_like(0))
        return self._ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        mask = self._ret.const_like(1) \
            .binary_op(BinaryOp.SUB, self._ret.binary_op(BinaryOp.CMP_EQ, self._ret.const_like(0)))
        return mask.binary_op(BinaryOp.MUL, grad_output)


class Log(Func):
    _x: LazyBuffer

    _mult: ta.Final[float] = math.log(2) / math.log(math.e)

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self._x = x
        return x.unary_op(UnaryOp.LOG2).binary_op(BinaryOp.MUL, x.const_like(self._mult))

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.binary_op(BinaryOp.DIV, self._x)


class Exp(Func):
    _ret: LazyBuffer

    _mult: ta.Final[float] = math.log(math.e) / math.log(2)

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self._ret = x.binary_op(BinaryOp.MUL, x.const_like(self._mult)).unary_op(UnaryOp.EXP2)
        return self._ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return self._ret.binary_op(BinaryOp.MUL, grad_output)


class Max(Func):
    _x: LazyBuffer
    _ret: LazyBuffer

    def forward(self, x: LazyBuffer, shape: Shape) -> LazyBuffer:
        self._x = x
        self._ret = x.reduce_op(ReduceOp.MAX, shape)
        return self._ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        # 1s in locations where the max was chosen (can be two locations)
        max_is_1s = self._x.binary_op(BinaryOp.CMP_EQ, self._ret.movement_op(MovementOp.EXPAND, self._x.shape))

        # sum of locations, averaged
        div = max_is_1s \
            .reduce_op(ReduceOp.SUM, grad_output.shape) \
            .movement_op(MovementOp.EXPAND, self._x.shape)

        max_is_amount = max_is_1s \
            .binary_op(BinaryOp.DIV, div)

        grad_output_expanded = grad_output.movement_op(MovementOp.EXPAND, self._x.shape)
        return max_is_amount.binary_op(BinaryOp.MUL, grad_output_expanded)
