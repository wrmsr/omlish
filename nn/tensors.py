import typing as ta

from omlish import check
from omlish import lang
import numpy as np

from .devices import DEFAULT_DEVICE  # noqa
from .devices import Device
from .dims import Shape
from .dtypes import Dtype
from .dtypes import Float32
from .funcs import Func
from .lazy import LazyBuffer
from .numpy import LazyNpArray


DEFAULT_DTYPE = Float32


class Tensor(lang.Final):
    def __init__(
            self,
            data: LazyBuffer,
            requires_grad: ta.Optional[bool],
    ) -> None:
        super().__init__()

        self._data = check.isinstance(data, LazyBuffer)
        self._requires_grad: ta.Optional[bool] = check.isinstance(requires_grad, (bool, None))

        self._grad: ta.Optional['Tensor'] = None
        self._func: ta.Optional[Func] = None

    @staticmethod
    def of(
            src: ta.Union[
                ta.Iterable,
                LazyBuffer,
                LazyNpArray,
                np.ndarray,
            ],
            *,
            device: ta.Optional[Device] = None,
            dtype: ta.Optional[Dtype] = None,
            **kwargs: ta.Any,
    ) -> 'Tensor':
        if device is None:
            device = DEFAULT_DEVICE

        if isinstance(src, list):
            src = np.array(src, dtype=(dtype or DEFAULT_DTYPE).np)

        if isinstance(src, LazyBuffer) and src.device != device:
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
