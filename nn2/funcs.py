import math
import typing as ta

from . import ops
from .dtypes import DType
from .helpers import argsort
from .lazy import LazyBuffer
from .shape.symbolic import sint
from .tensor import Function


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
    def forward(self, x: LazyBuffer, dtype: DType, bitcast: bool = False) -> LazyBuffer:
        self.input_dtype, self.bitcast = x.dtype, bitcast
        return x.e(ops.Cast, arg=(dtype, bitcast))

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.e(ops.Cast, arg=(self.input_dtype, self.bitcast))


# ************* unary ops *************


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
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self.x = x
        return x.e(ops.Sin)

    def backward(self, grad: LazyBuffer) -> LazyBuffer:
        return (
            self.x.const(math.pi / 2)
            .e(ops.Sub, self.x)
            .e(ops.Sin)
            .e(ops.Mul, grad)
        )


# NOTE: maximum(x, 0) behaves differently where x=0
class Relu(Function):
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self.ret = x.e(ops.Max2, x.const(0))
        return self.ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return (
            self.ret.const(0).e(ops.CmpLt, self.ret).e(ops.Mul, grad_output)
        )


class Log(Function):
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self.x = x
        return x.e(ops.Log2).e(ops.Mul, x.const(math.log(2)))

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.e(ops.Div, self.x)


class Exp(Function):
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self.ret = x.e(ops.Mul, x.const(1 / math.log(2))).e(ops.Exp2)
        return self.ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return self.ret.e(ops.Mul, grad_output)


class Sqrt(Function):
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self.ret = x.e(ops.Sqrt)
        return self.ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.e(
            ops.Div, self.ret.e(ops.Mul, self.ret.const(2))
        )


# NOTE: the implicit derivative of sigmoid is not stable
# https://towardsdatascience.com/derivative-of-the-sigmoid-function-536880cf918e
# TODO: have the backend automatically find this
class Sigmoid(Function):
    def forward(self, x: LazyBuffer) -> LazyBuffer:
        self.ret = x.const(1).e(
            ops.Div,
            x.const(1).e(
                ops.Add,
                x.e(ops.Mul, x.const(-1 / math.log(2))).e(ops.Exp2),
            ),
        )
        return self.ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return self.ret.e(
            ops.Mul, self.ret.const(1).e(ops.Sub, self.ret)
        ).e(ops.Mul, grad_output)


# ************* binary ops *************


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
    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        self.x, self.y = x, y
        return x.e(ops.Mul, y)

    def backward(
        self, grad_output: LazyBuffer
    ) -> tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            self.y.e(ops.Mul, grad_output) if self.needs_input_grad[0] else None,
            self.x.e(ops.Mul, grad_output) if self.needs_input_grad[1] else None,
        )


class Div(Function):
    def forward(self, x: LazyBuffer, y: LazyBuffer) -> LazyBuffer:
        self.x, self.y = x, y
        return x.e(ops.Div, y)

    def backward(
        self, grad_output: LazyBuffer
    ) -> tuple[ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            grad_output.e(ops.Div, self.y) if self.needs_input_grad[0] else None,
            grad_output.e(ops.Neg)
            .e(ops.Mul, self.x)
            .e(ops.Div, self.y.e(ops.Mul, self.y))
            if self.needs_input_grad[1]
            else None,
        )


# ************* ternary ops *************


class Where(Function):
    def forward(self, x: LazyBuffer, y: LazyBuffer, z: LazyBuffer) -> LazyBuffer:
        self.x = x
        return x.e(ops.Where, y, z)

    def backward(
        self, grad_output: LazyBuffer
    ) -> tuple[None, ta.Optional[LazyBuffer], ta.Optional[LazyBuffer]]:
        return (
            None,
            self.x.e(ops.Where, grad_output, grad_output.const(0))
            if self.needs_input_grad[1]
            else None,
            self.x.e(ops.Where, grad_output.const(0), grad_output)
            if self.needs_input_grad[2]
            else None,
        )


# ************* reduce ops *************


class Sum(Function):
    def forward(self, x: LazyBuffer, new_shape: tuple[int, ...]) -> LazyBuffer:
        self.input_shape = x.shape
        return x.r(ops.Sum, new_shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.expand(self.input_shape)


class Max(Function):
    def forward(self, x: LazyBuffer, new_shape: tuple[int, ...]) -> LazyBuffer:
        self.x, self.ret = x, x.r(ops.Max, new_shape)
        return self.ret

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        # 1s in locations where the max was chosen (can be two locations)
        max_is_1s = self.x.const(1.0).e(
            ops.Sub, self.x.e(ops.CmpLt, self.ret.expand(self.x.shape))
        )
        div = max_is_1s.r(ops.Sum, grad_output.shape).expand(self.x.shape)
        return max_is_1s.e(ops.Div, div).e(
            ops.Mul, grad_output.expand(self.x.shape)
        )


# ************* movement ops *************


# NOTE: this is sum in reverse
class Expand(Function):
    def forward(self, x: LazyBuffer, shape: tuple[int, ...]) -> LazyBuffer:
        self.input_shape = x.shape
        return x.expand(shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.r(ops.Sum, self.input_shape)


class Reshape(Function):
    def forward(self, x: LazyBuffer, shape: tuple[int, ...]) -> LazyBuffer:
        self.input_shape = x.shape
        return x.reshape(shape)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.reshape(self.input_shape)


class Permute(Function):
    def forward(self, x: LazyBuffer, order: tuple[int, ...]) -> LazyBuffer:
        self.input_order = order
        return x.permute(order)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.permute(argsort(self.input_order))


class Pad(Function):
    def forward(self, x: LazyBuffer, arg: tuple[tuple[int, int], ...]) -> LazyBuffer:
        self.narg = tuple([(p[0], s + p[0]) for s, p in zip(x.shape, arg)])
        return x.pad(arg)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.shrink(self.narg)


class Shrink(Function):
    def forward(self, x: LazyBuffer, arg: tuple[tuple[sint, sint], ...]) -> LazyBuffer:
        self.narg = tuple([(p[0], s - p[1]) for s, p in zip(x.shape, arg)])
        return x.shrink(arg)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        assert all(
            isinstance(x[0], int) and isinstance(x[1], int) for x in self.narg
        ), "symbolic shrink does not support backward"
        # need this cast because mypy cannot narrow the type even with assert
        return grad_output.pad(ta.cast(tuple[tuple[int, int], ...], self.narg))


class Flip(Function):
    def forward(self, x: LazyBuffer, axis: tuple[int, ...]) -> LazyBuffer:
        self.arg = tuple([-1 if i in set(axis) else 1 for i in range(len(x.shape))])
        return x.stride(self.arg)

    def backward(self, grad_output: LazyBuffer) -> LazyBuffer:
        return grad_output.stride(self.arg)
