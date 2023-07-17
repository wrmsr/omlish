import math
import typing as ta

from omlish import check
from omlish import lang
import numpy as np

from . import funcs
from . import ops
from .buffers import Buffer
from .devices import Device
from .devices import default_device  # noqa
from .dims import Shape
from .dims import Stride
from .dtypes import Dtype
from .dtypes import Float32
from .numpy import NumpyValue
from .numpy import np_to_scalar
from .scalars import SCALAR_TYPES
from .scalars import Scalar


DEFAULT_DTYPE = Float32


AxisLike = ta.Union[int, ta.Iterable[int]]

TensorLike = ta.Union[
    Scalar,
    ta.Iterable,
    Buffer,
    NumpyValue,
]

TensorOrLike = ta.Union['Tensor', TensorLike]


class Tensor(lang.Final):
    def __init__(
            self,
            src: TensorLike,
            requires_grad: ta.Optional[bool] = None,
            *,
            device: ta.Optional[Device] = None,
            dtype: ta.Optional[Dtype] = None,

            func: ta.Optional[funcs.Func] = None,
    ) -> None:
        check.not_isinstance(src, (Shape, Stride))

        super().__init__()

        if device is None:
            device = default_device()

        data: Buffer

        if isinstance(src, Buffer):
            check.arg(dtype is None or dtype == src.dtype)
            data = src

        elif isinstance(src, SCALAR_TYPES):
            data = Buffer.load_op(
                ops.Const,
                Shape(),
                (dtype or DEFAULT_DTYPE),
                device,
                src,
            )

        else:
            if isinstance(src, ta.Iterable):
                src = np.array(src, dtype=(dtype or DEFAULT_DTYPE).np)

            if isinstance(src, np.ndarray):
                if src.size == 1:
                    data = Buffer.load_op(
                        ops.Const,
                        Shape(),
                        Dtype.of_np(src.dtype),
                        device,
                        np_to_scalar(src.flat[0]),
                    ).movement_op(
                        ops.Reshape,
                        Shape(src.shape),
                    )
                else:
                    data = Buffer.from_cpu(src)

            else:
                raise TypeError(src)

        if data.device != device:
            data = Buffer.load_op(
                ops.From,
                data.shape,
                data.dtype,
                device,
                src=data,
            )

        self._data = check.isinstance(data, Buffer)
        self._requires_grad: ta.Optional[bool] = check.isinstance(requires_grad, (bool, None))

        self._grad: ta.Optional['Tensor'] = None
        self._func: ta.Optional[funcs.Func] = check.isinstance(func, (funcs.Func, None))
        self._had_func = func is not None

    # Accessors

    @property
    def data(self) -> Buffer:
        return self._data

    @property
    def device(self) -> Device:
        return self._data.device

    @property
    def shape(self) -> Shape:
        return self._data.shape

    @property
    def dtype(self) -> Dtype:
        return self._data.dtype

    @property
    def requires_grad(self) -> ta.Optional[bool]:
        return self._requires_grad

    def set_requires_grad(self, b: bool) -> 'Tensor':
        check.none(self._requires_grad)
        self._requires_grad = b
        return self

    def get_grad(self) -> 'Tensor':
        return check.not_none(self._grad)

    def zero_grad(self) -> None:
        self._grad = None

    # Creators

    @staticmethod
    def of(src: TensorOrLike) -> 'Tensor':
        if isinstance(src, Tensor):
            return src
        else:
            return Tensor(src)

    @staticmethod
    def full(shape: Shape, fill_value: Scalar, **kwargs: ta.Any) -> 'Tensor':
        return Tensor(fill_value, **kwargs) \
            .reshape(*([1] * len(shape))) \
            .expand(*shape) \
            .contiguous()

    @staticmethod
    def full_like(tensor: 'Tensor', fill_value, dtype: ta.Optional[Dtype] = None, **kwargs: ta.Any) -> 'Tensor':
        return Tensor.full(
            tensor.shape,
            fill_value=fill_value,
            dtype=tensor.dtype if dtype is None else dtype,
            **kwargs,
        )

    @staticmethod
    def zeros(*shape: int, **kwargs: ta.Any) -> 'Tensor':
        return Tensor.full(Shape(shape), 0, **kwargs)

    @staticmethod
    def ones(*shape: int, **kwargs: ta.Any) -> 'Tensor':
        return Tensor.full(Shape(shape), 1, **kwargs)

    @staticmethod
    def _load_op(
            op: ta.Type[ops.LoadOp],
            sz: int,
            device: ta.Optional[Device] = None,
            dtype: ta.Optional[Dtype] = None,
            arg: ta.Any = None,
            **kwargs: ta.Any
    ) -> 'Tensor':
        return Tensor(
            Buffer.load_op(
                op,
                Shape(sz),
                dtype or DEFAULT_DTYPE,
                device or default_device(),
                arg,
            ),
            dtype=dtype,
            device=device,
            **kwargs,
        )

    @staticmethod
    def empty(*shape: int, **kwargs: ta.Any) -> 'Tensor':
        return Tensor._load_op(ops.Empty, math.prod(shape), **kwargs).reshape(*shape)

    #

    def realize(self) -> 'Tensor':
        self._data.realize()
        return self

    def assign(self, x: TensorOrLike) -> 'Tensor':
        x = Tensor.of(x)
        check.arg(self.shape == x.shape, f'assign shape mismatch {self.shape} != {x.shape}')
        check.state(not x.requires_grad)
        if self._data._realized is not None:  # FIXME: ???
            x._data._output_buffer = self._data._realized  # FIXME: ???
        self._data = x._data
        return self

    def detach(self) -> 'Tensor':
        return Tensor(self._data, device=self.device, requires_grad=False)

    def numpy(self) -> NumpyValue:
        return self._data.to_cpu()

    def reshape(self, *shape: int) -> 'Tensor':
        check.arg(all(check.isinstance(x, int) != 0 for x in shape))
        return funcs.Reshape.apply(
            self,
            shape=Shape(-self.shape.prod // math.prod(shape) if s == -1 else s for s in shape)
        )

    def expand(self, *shape: int) -> 'Tensor':
        check.arg(all(check.isinstance(x, int) for x in shape))
        return funcs.Expand.apply(
            self,
            shape=Shape(x if x != -1 else s for s, x in zip(self.shape, shape))
        )

    def _broadcasted(
            self,
            func: ta.Type[funcs.Func],
            other: TensorOrLike,
            reverse: bool = False,
    ) -> 'Tensor':
        x = self
        y = Tensor.of(other)
        if reverse:
            x, y = y, x
        if x.shape == y.shape:
            return func.apply(x, y)

        len_x_shape, len_y_shape = len(x.shape), len(y.shape)
        max_shape = max(len_x_shape, len_y_shape)

        if len_x_shape != max_shape:
            x = x.reshape(*((1,) * (max_shape - len_x_shape) + x.shape))
        if len_y_shape != max_shape:
            y = y.reshape(*((1,) * (max_shape - len_y_shape) + y.shape))

        shape_ret = [max(x, y) for x, y in zip(x.shape, y.shape)]
        if x.shape != shape_ret:
            x = x.expand(*shape_ret)
        if y.shape != shape_ret:
            y = y.expand(*shape_ret)

        return func.apply(x, y)

    def add(self, x: TensorOrLike, reverse: bool = False) -> 'Tensor':
        return self._broadcasted(funcs.Add, x, reverse)

    def sub(self, x: TensorOrLike, reverse: bool = False) -> 'Tensor':
        return self._broadcasted(funcs.Sub, x, reverse)

    def mul(self, x: TensorOrLike, reverse: bool = False) -> 'Tensor':
        return self._broadcasted(funcs.Mul, x, reverse)

    def div(self, x: TensorOrLike, reverse: bool = False) -> 'Tensor':
        return self._broadcasted(funcs.Div, x, reverse)

    def square(self) -> 'Tensor':
        return self * self

    def sum(self, axis: ta.Optional[AxisLike] = None, keepdim: bool = False) -> 'Tensor':
        return self._reduce(funcs.Sum, axis, keepdim)

    def mean(self, axis: ta.Optional[AxisLike] = None, keepdim: bool = False) -> 'Tensor':
        out = self.sum(axis=axis, keepdim=keepdim)
        return out * (out.shape.prod / self.shape.prod)

    def __neg__(self) -> 'Tensor':
        return 0.0 - self

    def __add__(self, other: TensorOrLike) -> 'Tensor':
        return self.add(other)

    def __radd__(self, other: TensorOrLike) -> 'Tensor':
        return self.add(other, reverse=True)

    def __sub__(self, other: TensorOrLike) -> 'Tensor':
        return self.sub(other)

    def __rsub__(self, other: TensorOrLike) -> 'Tensor':
        return self.sub(other, reverse=True)

    def __mul__(self, other: TensorOrLike) -> 'Tensor':
        return self.mul(other)

    def __rmul__(self, other: TensorOrLike) -> 'Tensor':
        return self.mul(other, reverse=True)

    def __truediv__(self, other: TensorOrLike) -> 'Tensor':
        return self.div(other)

    def __rtruediv__(self, other: TensorOrLike) -> 'Tensor':
        return self.div(other, reverse=True)

    def _reduce(
            self,
            func: ta.Type[funcs.Func],
            axis: ta.Optional[AxisLike] = None,
            keepdim: bool = False,
    ) -> 'Tensor':
        ax: ta.List[int]
        if axis is None:
            ax = list(range(len(self.shape)))
        elif isinstance(axis, int):
            ax = [axis]
        else:
            ax = list(axis)

        ax = [
            x if x >= 0 else x + len(self.shape)
            for x in ax
        ]

        shape = [
            self.shape[i]
            for i in range(len(self.shape))
            if i not in ax
        ]

        ret = func.apply(
            self,
            shape=Shape(
                1 if i in ax else self.shape[i]
                for i in range(len(self.shape))
            ),
        )

        if keepdim:
            return ret

        return ret.reshape(*shape)

    def contiguous(self) -> 'Tensor':
        return funcs.Contiguous.apply(self)

    def deep_walk(self) -> ta.Sequence['Tensor']:
        nodes: ta.List[Tensor] = []
        visited = set()

        def rec(node: 'Tensor') -> None:
            visited.add(node)
            if node._func:
                for i in node._func.parents:
                    if i not in visited:
                        rec(i)
                nodes.append(node)

        rec(self)
        return nodes

    def backward(self) -> None:
        check.state(not self.shape)

        # fill in the first grad with one. don't use Tensor.ones because we don't need contiguous - this is "implicit
        # gradient creation"
        self._grad = Tensor(1, device=self.device, requires_grad=False)

        for cur in reversed(self.deep_walk()):
            cur_func = check.not_none(cur._func)
            if not cur.requires_grad:  # any(x.requires_grad for x in cur_func.parents):
                del cur._func  # TODO: does it help to delete this here ever?
                continue

            grads = cur_func.backward(check.not_none(cur._grad)._data)
            grads = [
                Tensor(g, device=self.device, requires_grad=False) if g is not None else None
                for g in ([grads] if len(cur_func.parents) == 1 else grads)
            ]

            for p, g in zip(cur_func.parents, grads):
                if g is not None and p.requires_grad:
                    check.state(g.shape == p.shape, f'grad shape must match tensor shape, {g.shape!r} != {p.shape!r}')
                    if p._grad is None:
                        p._grad = g
                    else:
                        p._grad = p._grad + g

            del cur._func

    def permute(self, *order: int) -> 'Tensor':
        check.arg(sorted(order) == list(range(len(order))))
        return funcs.Permute.apply(self, order=order)

    def transpose(self, ax1: int = 1, ax2: int = 0) -> 'Tensor':
        order = list(range(len(self.shape)))
        order[ax1], order[ax2] = order[ax2], order[ax1]
        return self.permute(*order)

    def dot(self, w: 'Tensor') -> 'Tensor':
        check.arg(((n1 := len(self.shape)) * (n2 := len(w.shape))) != 0)
        x = self.reshape(*self.shape[0:-1], *[1] * min(n1 - 1, n2 - 1, 1), self.shape[-1])
        w = w.reshape(*w.shape[0:-2], *[1] * min(n1 - 1, n2 - 1, 1), *w.shape[-min(n2, 2):]).transpose(-1, -min(n2, 2))
        return (x * w).sum(-1)

    def matmul(self, x: 'Tensor', reverse: bool = False) -> 'Tensor':
        return x.dot(self) if reverse else self.dot(x)

    def log(self) -> 'Tensor':
        return funcs.Log.apply(self)

    def exp(self) -> 'Tensor':
        return funcs.Exp.apply(self)

    def relu(self) -> 'Tensor':
        return funcs.Relu.apply(self)

    def max(self, axis: ta.Optional[AxisLike] = None, keepdim: bool = False) -> 'Tensor':
        return self._reduce(funcs.Max, axis, keepdim)

    class _Softmax(ta.NamedTuple):
        m: 'Tensor'
        e: 'Tensor'
        ss: 'Tensor'

    def _softmax(self, axis: AxisLike) -> _Softmax:
        m = self - self.max(axis=axis, keepdim=True)
        e = m.exp()
        return Tensor._Softmax(m, e, e.sum(axis=axis, keepdim=True))

    def softmax(self, axis: AxisLike = -1) -> 'Tensor':
        sm = self._softmax(axis)
        return sm.e.div(sm.ss)

    def log_softmax(self, axis: AxisLike = -1) -> 'Tensor':
        sm = self._softmax(axis)
        return sm.m - sm.ss.log()
