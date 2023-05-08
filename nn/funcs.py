import abc
import typing as ta

from omlish import lang

from .lazy import LazyBuffer
from .ops import BinaryOp


if ta.TYPE_CHECKING:
    from .tensors import Tensor


class Func(lang.Abstract):

    def __init__(self, *parents: Tensor) -> None:
        super().__init__()

        self._parents = parents  # [check.isinstance(p, Tensor) for p in parents]

        self._needs_input_grad = [t.requires_grad for t in parents]

        self._requires_grad: ta.Optional[bool] = None
        if any(self._needs_input_grad):
            self._requires_grad = True
        elif not any(x is None for x in self._needs_input_grad):
            self._requires_grad = False

    @abc.abstractmethod
    def forward(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def backward(self, *args, **kwargs):
        raise NotImplementedError


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
