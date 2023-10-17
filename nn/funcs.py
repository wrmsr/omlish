from __future__ import annotations

import math
import typing as ta

from omlish import lang

from . import ops
from .dtypes import DType
from .helpers import argsort
from .lazy import LazyBuffer
from .shape.symbolic import sint

if ta.TYPE_CHECKING:
    from . import tensor
else:
    tensor = lang.proxy_import('.tensor', __package__)


##


# An instantiation of the Function is the Context
class Function:
    def __init__(self, device: str, *tensors: tensor.Tensor) -> None:
        super().__init__()
        self.device = device
        self.needs_input_grad = [t.requires_grad for t in tensors]
        self.requires_grad = (
            True if any(self.needs_input_grad) else
            None if None in self.needs_input_grad else
            False
        )
        if self.requires_grad:
            self.parents = tensors

    def forward(self, *args, **kwargs):
        raise NotImplementedError(f"forward not implemented for {type(self)}")

    def backward(self, *args, **kwargs):
        raise RuntimeError(f"backward not implemented for {type(self)}")

    @classmethod
    def apply(fxn: type[Function], *x: tensor.Tensor, **kwargs) -> tensor.Tensor:
        ctx = fxn(x[0].device, *x)
        ret = tensor.Tensor(
            ctx.forward(*[t.lazydata for t in x], **kwargs),
            device=ctx.device,
            requires_grad=ctx.requires_grad,
        )
        if ctx.requires_grad and not tensor.Tensor.no_grad:
            ret._ctx = ctx  # used by autograd engine
        return ret


##


class Contiguous(Function):
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        return x.contiguous()

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output


class ContiguousBackward(Function):
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        return x

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.contiguous()


class Cast(Function):
    _input_dtype: LazyBuffer
    _bitcast: bool

    def forward(self, x: LazyBuffer, dtype: DType, bitcast: bool = False) -> LazyBuffer:
        self._input_dtype = x.dtype
        self._bitcast = bitcast
        return x.e(ops.Cast, arg=(dtype, bitcast))

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.e(ops.Cast, arg=(self._input_dtype, self._bitcast))


# UnaryOps


class Zero(Function):
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        return x.const(0)

    def backward(self, grad: LazyBuffer) -> LazyBuffer:
        return grad.const(0)


class Neg(Function):
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        return x.e(ops.Neg)

    def backward(self, grad: LazyBuffer) -> LazyBuffer:
        return grad.e(ops.Neg)


class Sin(Function):
    _x: LazyBuffer

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self._x = x
        return x.e(ops.Sin)

    def backward(self, grad: LazyBuffer) -> LazyBuffer:
        return (
            self._x.const(math.pi / 2)
            .e(ops.Sub, self._x)
            .e(ops.Sin)
            .e(ops.Mul, grad)
        )


# NOTE: maximum(x, 0) behaves differently where x=0
class Relu(Function):
    _ret: LazyBuffer

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self._ret = x.e(ops.Max2, x.const(0))
        return self._ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return (
            self._ret.const(0).e(ops.CmpLt, self._ret).e(ops.Mul, grad_output)
        )


class Log(Function):
    _x: LazyBuffer

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self._x = x
        return x.e(ops.Log2).e(ops.Mul, x.const(math.log(2)))

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.e(ops.Div, self._x)


class Exp(Function):
    _ret: LazyBuffer

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self._ret = x.e(ops.Mul, x.const(1 / math.log(2))).e(ops.Exp2)
        return self._ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return self._ret.e(ops.Mul, grad_output)


class Sqrt(Function):
    _ret: LazyBuffer

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self._ret = x.e(ops.Sqrt)
        return self._ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.e(
            ops.Div, self._ret.e(ops.Mul, self._ret.const(2))
        )


# NOTE: the implicit derivative of sigmoid is not stable
# https://towardsdatascience.com/derivative-of-the-sigmoid-function-536880cf918e
# TODO: have the backend automatically find this
class Sigmoid(Function):
    _ret: LazyBuffer

    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self._ret = x.const(1).e(
            ops.Div,
            x.const(1).e(
                ops.Add,
                x.e(ops.Mul, x.const(-1 / math.log(2))).e(ops.Exp2),
            ),
        )
        return self._ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return self._ret.e(
            ops.Mul, self._ret.const(1).e(ops.Sub, self._ret)
        ).e(ops.Mul, grad_output)


# BinaryOps


class Less(Function):
    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        return x.e(ops.CmpLt, y)


class Add(Function):
    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        return x.e(ops.Add, y)

    def backward(
        self, grad_output: LazyBuffer
    ) -> tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            grad_output if self.needs_input_grad[0] else None,
            grad_output if self.needs_input_grad[1] else None,
        )


class Sub(Function):
    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        return x.e(ops.Sub, y)

    def backward(
        self, grad_output: LazyBuffer
    ) -> tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            grad_output if self.needs_input_grad[0] else None,
            grad_output.e(ops.Neg) if self.needs_input_grad[1] else None,
        )


class Mul(Function):
    _x: LazyBuffer
    _y: LazyBuffer

    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        self._x = x
        self._y = y
        return x.e(ops.Mul, y)

    def backward(
        self, grad_output: LazyBuffer
    ) -> tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            self._y.e(ops.Mul, grad_output) if self.needs_input_grad[0] else None,
            self._x.e(ops.Mul, grad_output) if self.needs_input_grad[1] else None,
        )


class Div(Function):
    _x: LazyBuffer
    _y: LazyBuffer

    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        self._x = x
        self._y = y
        return x.e(ops.Div, y)

    def backward(
        self, grad_output: LazyBuffer
    ) -> tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            grad_output.e(ops.Div, self._y) if self.needs_input_grad[0] else None,
            grad_output.e(ops.Neg)
            .e(ops.Mul, self._x)
            .e(ops.Div, self._y.e(ops.Mul, self._y))
            if self.needs_input_grad[1]
            else None,
        )


# TernaryOps


class Where(Function):
    _x: LazyBuffer

    def forward(self, x: LazyBuffer, y: LazyBuffer, z: LazyBuffer) -> LazyBuffer:
        self._x = x
        return x.e(ops.Where, y, z)

    def backward(
        self, grad_output: LazyBuffer
    ) -> tuple[None, ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            None,
            self._x.e(ops.Where, grad_output, grad_output.const(0)) if self.needs_input_grad[1] else None,
            self._x.e(ops.Where, grad_output.const(0), grad_output) if self.needs_input_grad[2] else None,
        )


# ReduceOps


class Sum(Function):
    _input_shape: tuple[sint, ...]

    def forward(self, x: LazyBuffer, new_shape: tuple[int, ...]) -> LazyBuffer:
        self._input_shape = x.shape
        return x.r(ops.Sum, new_shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.expand(self._input_shape)


class Max(Function):
    _x: LazyBuffer
    _ret: LazyBuffer

    def forward(self, x: LazyBuffer, new_shape: tuple[int, ...]) -> LazyBuffer:
        self._x = x
        self._ret = x.r(ops.Max, new_shape)
        return self._ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        # 1s in locations where the max was chosen (can be two locations)
        max_is_1s = self._x.const(1.0).e(
            ops.Sub, self._x.e(ops.CmpLt, self._ret.expand(self._x.shape))
        )
        div = max_is_1s.r(ops.Sum, grad_output.shape).expand(self._x.shape)
        return max_is_1s.e(ops.Div, div).e(
            ops.Mul, grad_output.expand(self._x.shape)
        )


# MovementOps


# NOTE: this is sum in reverse
class Expand(Function):
    _input_shape: tuple[sint, ...]

    def forward(self, x: LazyBuffer, shape: tuple[int, ...]) -> LazyBuffer:
        self._input_shape = x.shape
        return x.expand(shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.r(ops.Sum, self._input_shape)


class Reshape(Function):
    _input_shape: tuple[sint, ...]

    def forward(self, x: LazyBuffer, shape: tuple[int, ...]) -> LazyBuffer:
        self._input_shape = x.shape
        return x.reshape(shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.reshape(self._input_shape)


class Permute(Function):
    _input_order: tuple[int, ...]

    def forward(self, x: LazyBuffer, order: tuple[int, ...]) -> LazyBuffer:
        self._input_order = order
        return x.permute(order)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.permute(argsort(self._input_order))


class Pad(Function):
    _narg: tuple[tuple[sint, sint], ...]

    def forward(self, x: LazyBuffer, arg: tuple[tuple[int, int], ...]) -> LazyBuffer:
        self._narg = tuple([(p[0], s + p[0]) for s, p in zip(x.shape, arg)])
        return x.pad(arg)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.shrink(self._narg)


class Shrink(Function):
    _narg: tuple[tuple[sint, sint], ...]

    def forward(self, x: LazyBuffer, arg: tuple[tuple[sint, sint], ...]) -> LazyBuffer:
        self._narg = tuple([(p[0], s - p[1]) for s, p in zip(x.shape, arg)])
        return x.shrink(arg)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        assert all(
            isinstance(x[0], int) and isinstance(x[1], int) for x in self._narg
        ), "symbolic shrink does not support backward"
        # need this cast because mypy cannot narrow the type even with assert
        return grad_output.pad(ta.cast(tuple[tuple[int, int], ...], self._narg))


class Flip(Function):
    _arg: tuple[int, ...]

    def forward(self, x: LazyBuffer, axis: tuple[int, ...]) -> LazyBuffer:
        self._arg = tuple([-1 if i in set(axis) else 1 for i in range(len(x.shape))])
        return x.stride(self._arg)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.stride(self._arg)
