import typing as ta

from omlish import check
from omlish import lang
import numpy as np

from . import funcs
from .devices import DEFAULT_DEVICE  # noqa
from .devices import Device
from .dims import Shape
from .dtypes import Dtype
from .dtypes import Float32
from .lazy import LazyBuffer
from .numpy import LazyNpArray


DEFAULT_DTYPE = Float32


TensorLike = ta.Union[
    'Tensor',
    float,
    ta.Iterable,
    LazyBuffer,
    LazyNpArray,
    np.ndarray,
]


class Tensor(lang.Final):
    def __init__(
            self,
            data: LazyBuffer,
            requires_grad: ta.Optional[bool] = None,
            *,
            func: ta.Optional[funcs.Func] = None,
    ) -> None:
        super().__init__()

        self._data = check.isinstance(data, LazyBuffer)
        self._requires_grad: ta.Optional[bool] = check.isinstance(requires_grad, (bool, None))

        self._grad: ta.Optional['Tensor'] = None
        self._func: ta.Optional[funcs.Func] = check.isinstance(func, (funcs.Func, None))
        self._had_func = func is not None

    @staticmethod
    def of(
            src: TensorLike,
            *,
            device: ta.Optional[Device] = None,
            dtype: ta.Optional[Dtype] = None,

            requires_grad: ta.Optional[bool] = None,
            **kwargs: ta.Any,
    ) -> 'Tensor':
        if device is None:
            device = DEFAULT_DEVICE

        if isinstance(src, Tensor):
            if src.device != device:
                raise NotImplementedError
            return src

        if isinstance(src, list):
            src = np.array(src, dtype=(dtype or DEFAULT_DTYPE).np)

        elif isinstance(src, (int, float)):
            src = np.array([src], dtype=(dtype or DEFAULT_DTYPE).np)

        elif isinstance(src, LazyBuffer) and src.device != device:
            # FIXME:
            raise NotImplementedError

        if isinstance(src, np.ndarray):
            src = LazyNpArray(src, Shape(src.shape), Dtype.of_np(src.dtype))

        if isinstance(src, LazyNpArray):
            if not src.shape:
                # FIXME: ??
                src = src.reshape(Shape(1, ))
            if dtype is not None:
                src = src.astype(dtype.np)
            data = LazyBuffer.from_cpu(src, device)

        elif isinstance(src, LazyBuffer):
            check.arg(dtype is None or dtype == src.dtype)
            data = src

        else:
            raise TypeError(src)

        if dtype is not None and data.dtype != dtype:
            raise NotImplementedError

        return Tensor(
            data,
            requires_grad=requires_grad,
            **kwargs,
        )

    @property
    def data(self) -> LazyBuffer:
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

    def get_grad(self) -> 'Tensor':
        return check.not_none(self._grad)

    ##

    def realize(self) -> 'Tensor':
        self._data.realize()
        return self

    def numpy(self) -> np.ndarray:
        return self._data.to_cpu()

    def reshape(self, shape: Shape) -> 'Tensor':
        check.arg(shape and all(x != 0 for x in shape), f'Zeros not allowed in shape {shape}')
        return funcs.Reshape.apply(
            self,
            shape=Shape(-self.shape.prod // shape.prod if s == -1 else s for s in shape)
        )

    def expand(self, shape: Shape) -> 'Tensor':
        return funcs.Expand.apply(
            self,
            shape=Shape(x if x != -1 else s for s, x in zip(self.shape, shape))
        )

    def _broadcasted(
            self,
            func: ta.Type[funcs.Func],
            other: TensorLike,
            reverse: bool = False,
    ) -> 'Tensor':
        other = Tensor.of(other)
        x, y = (other, self) if reverse else (self, other)

        x, y = [
            t.reshape(Shape([1] * (max(len(x.shape), len(y.shape)) - len(t.shape)) + list(t.shape)))
            for t in [x, y]
        ]

        ret_shape = Shape(max(sx, sy) for sx, sy in zip(x.shape, y.shape))

        return func.apply(x.expand(ret_shape), y.expand(ret_shape))

    def add(self, x: TensorLike, reverse=False) -> 'Tensor':
        return self._broadcasted(funcs.Add, x, reverse)

    def mul(self, x: TensorLike, reverse=False) -> 'Tensor':
        return self._broadcasted(funcs.Mul, x, reverse)

    def square(self) -> 'Tensor':
        return self * self

    def sum(
            self,
            axis: ta.Union[int, ta.Iterable[int], None] = None,
            keepdim: bool = False,
    ) -> 'Tensor':
        return self._reduce(funcs.Sum, axis, keepdim)

    def mean(
            self,
            axis: ta.Union[int, ta.Iterable[int], None] = None,
            keepdim: bool = False,
    ) -> 'Tensor':
        out = self.sum(axis=axis, keepdim=keepdim)
        return out * (out.shape.prod / self.shape.prod)

    def __add__(self, other: TensorLike) -> 'Tensor':
        return self.add(other)

    def __mul__(self, other: TensorLike) -> 'Tensor':
        return self.mul(other)

    def _reduce(
            self,
            func: ta.Type[funcs.Func],
            axis: ta.Union[int, ta.Iterable[int], None] = None,
            keepdim=False,
    ):
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

        return ret.reshape(Shape([1] if not shape else shape))

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
        check.state(self.shape == Shape(1))

        # fill in the first grad with one. don't use Tensor.ones because we don't need contiguous - this is "implicit
        # gradient creation"
        self._grad = Tensor.of([1], device=self.device, requires_grad=False)

        for cur in reversed(self.deep_walk()):
            cur_func = check.not_none(cur._func)
            if not any(x.requires_grad for x in cur_func.parents):
                del cur._func  # TODO: does it help to delete this here ever?
                continue

            grads = cur_func.backward(check.not_none(cur._grad)._data)
            grads = [
                Tensor.of(g, device=self.device, requires_grad=False) if g is not None else None
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
