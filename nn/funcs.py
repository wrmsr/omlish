import abc
import math
import typing as ta

from omlish import check
from omlish import lang

from . import ops
from .buffers import Buffer
from .devices import Device
from .dims import Shape


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
        ret = tensor.Tensor(
            func.forward(*[t.data for t in args], **kwargs),
            device=func.device,
            requires_grad=func.requires_grad,
            func=func,
        )
        return ret


##


class Add(Func):
    _x: Buffer
    _y: Buffer

    def forward(self, x: Buffer, y: Buffer) -> Buffer:
        self._x = x
        self._y = y
        return x.binary_op(ops.Add, y)

    def backward(self, grad_output: Buffer) -> ta.Tuple[ta.Optional[Buffer], ta.Optional[Buffer]]:
        return (
            grad_output if self._needs_input_grad[0] else None,
            grad_output if self._needs_input_grad[1] else None,
        )


class Sub(Func):

    def forward(self, x: Buffer, y: Buffer) -> Buffer:
        return x.binary_op(ops.Sub, y)

    def backward(self, grad_output: Buffer) -> ta.Tuple[ta.Optional[Buffer], ta.Optional[Buffer]]:
        return (
            grad_output if self.needs_input_grad[0] else None,
            grad_output.const_like(0).binary_op(ops.Sub, grad_output) if self.needs_input_grad[1] else None,
        )


class Mul(Func):
    _x: Buffer
    _y: Buffer

    def forward(self, x: Buffer, y: Buffer) -> Buffer:
        self._x = x
        self._y = y
        return x.binary_op(ops.Mul, y)

    def backward(self, grad_output: Buffer) -> ta.Tuple[ta.Optional[Buffer], ta.Optional[Buffer]]:
        return (
            self._y.binary_op(ops.Mul, grad_output) if self._needs_input_grad[0] else None,
            self._x.binary_op(ops.Mul, grad_output) if self._needs_input_grad[1] else None,
        )


class Div(Func):
    _x: Buffer
    _y: Buffer

    def forward(self, x: Buffer, y: Buffer) -> Buffer:
        self._x = x
        self._y = y
        return x.binary_op(ops.Div, y)

    def backward(self, grad_output: Buffer) -> ta.Tuple[ta.Optional[Buffer], ta.Optional[Buffer]]:
        return (
            grad_output.binary_op(ops.Div, self._y) if self.needs_input_grad[0] else None,
            (
                grad_output
                .const_like(0)
                .binary_op(ops.Sub, grad_output)
                .binary_op(ops.Mul, self._x)
                .binary_op(ops.Div, self._y.binary_op(ops.Mul, self._y))
            ) if self.needs_input_grad[1] else None
        )


##


class Expand(Func):
    _input_shape: Shape

    def forward(self, x: Buffer, shape: Shape) -> Buffer:
        self._input_shape = x.shape
        return x.movement_op(ops.Expand, shape)

    def backward(self, grad_output: Buffer) -> Buffer:
        return grad_output.reduce_op(ops.Sum, self._input_shape)


class Reshape(Func):
    _input_shape: Shape

    def forward(self, x: Buffer, shape: Shape) -> Buffer:
        self._input_shape = x.shape
        return x.movement_op(ops.Reshape, shape)

    def backward(self, grad_output: Buffer) -> Buffer:
        return grad_output.movement_op(ops.Reshape, self._input_shape)


class Sum(Func):
    _input_shape: Shape

    def forward(self, x: Buffer, shape: Shape) -> Buffer:
        self._input_shape = x.shape
        return x.reduce_op(ops.Sum, shape)

    def backward(self, grad_output: Buffer) -> Buffer:
        return grad_output.movement_op(ops.Expand, self._input_shape)


class Contiguous(Func):

    def forward(self, x: Buffer) -> Buffer:
        return x.contiguous()

    def backward(self, grad_output: Buffer) -> Buffer:
        return grad_output


class Permute(Func):
    _input_order: ta.Sequence[int]

    def forward(self, x: Buffer, order: ta.Sequence[int]) -> Buffer:
        self._input_order = order
        return x.movement_op(ops.Permute, order)

    def backward(self, grad_output: Buffer) -> Buffer:
        output_order = tuple(t[0] for t in sorted(enumerate(self._input_order), key=lambda t: t[1]))
        return grad_output.movement_op(ops.Permute, output_order)


class Relu(Func):
    _ret: Buffer

    def forward(self, x: Buffer) -> Buffer:
        self._ret = x.binary_op(ops.Maximum, x.const_like(0))
        return self._ret

    def backward(self, grad_output: Buffer) -> Buffer:
        mask = self._ret.const_like(1) \
            .binary_op(ops.Sub, self._ret.binary_op(ops.CmpEq, self._ret.const_like(0)))
        return mask.binary_op(ops.Mul, grad_output)


##


class Log(Func):
    _x: Buffer

    _mult: ta.Final[float] = math.log(2)

    def forward(self, x: Buffer) -> Buffer:
        self._x = x
        return x.unary_op(ops.Log2).binary_op(ops.Mul, x.const_like(self._mult))

    def backward(self, grad_output: Buffer) -> Buffer:
        return grad_output.binary_op(ops.Div, self._x)


class Exp(Func):
    _ret: Buffer

    _mult: ta.Final[float] = 1 / math.log(2)

    def forward(self, x: Buffer) -> Buffer:
        self._ret = x.binary_op(ops.Mul, x.const_like(self._mult)).unary_op(ops.Exp2)
        return self._ret

    def backward(self, grad_output: Buffer) -> Buffer:
        return self._ret.binary_op(ops.Mul, grad_output)


class Sqrt(Func):
    _ret: Buffer

    def forward(self, x: Buffer) -> Buffer:
        self._ret = x.unary_op(ops.Sqrt)
        return self._ret

    def backward(self, grad_output: Buffer) -> Buffer:
        return grad_output.binary_op(ops.Div, self._ret.binary_op(ops.Mul, self._ret.const_like(2)))


class Sigmoid(Func):
    _ret: Buffer

    _mult: ta.Final[float] = -1 / math.log(2)

    def forward(self, x: Buffer) -> Buffer:
        self._ret = x.const_like(
            1,
        ).binary_op(
            ops.Div,
            x.const_like(1).binary_op(
                ops.Add,
                x.binary_op(
                    ops.Mul,
                    x.const_like(self._mult),
                ).unary_op(ops.Exp2)))  # noqa
        return self._ret

    def backward(self, grad_output: Buffer) -> Buffer:
        return self._ret.binary_op(
            ops.Mul,
            self._ret.const_like(1).binary_op(
                ops.Sub,
                self._ret,
            ),
        ).binary_op(
            ops.Mul,
            grad_output,
        )


class Max(Func):
    _x: Buffer
    _ret: Buffer

    def forward(self, x: Buffer, shape: Shape) -> Buffer:
        self._x = x
        self._ret = x.reduce_op(ops.Max, shape)
        return self._ret

    def backward(self, grad_output: Buffer) -> Buffer:
        # 1s in locations where the max was chosen (can be two locations)
        max_is_1s = self._x.binary_op(ops.CmpEq, self._ret.movement_op(ops.Expand, self._x.shape))

        # sum of locations, averaged
        div = max_is_1s \
            .reduce_op(ops.Sum, grad_output.shape) \
            .movement_op(ops.Expand, self._x.shape)

        max_is_amount = max_is_1s \
            .binary_op(ops.Div, div)

        grad_output_expanded = grad_output.movement_op(ops.Expand, self._x.shape)
        return max_is_amount.binary_op(ops.Mul, grad_output_expanded)
