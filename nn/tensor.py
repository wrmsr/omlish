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
            **kwargs: ta.Any,
    ) -> 'Tensor':
        if device is None:
            device = DEFAULT_DEVICE

        if isinstance(src, Tensor):
            if src.device != device:
                raise NotImplementedError
            return src

        if isinstance(src, list):  # FIXME
            src = np.array(src, dtype=(dtype or DEFAULT_DTYPE).np)

        elif isinstance(src, float):
            raise NotImplementedError

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

        return Tensor(data, **kwargs)

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

    ##

    def realize(self) -> 'Tensor':
        self._data.realize()
        return self

    def numpy(self) -> np.ndarray:
        return self._data.to_cpu()

    def reshape(self, shape: Shape) -> 'Tensor':
        check.arg(len(shape) > 0 and all(x != 0 for x in shape), f'Zeros not allowed in shape {shape}')
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

    def mul(self, x: TensorLike, reverse=False) -> 'Tensor':
        return self._broadcasted(funcs.Mul, x, reverse)

    def __mul__(self, other: TensorLike) -> 'Tensor':
        return self.mul(other)
