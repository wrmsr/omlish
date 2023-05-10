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
from .numpy import LazyNumpyArray  # noqa


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
            data: ta.Union[ta.Iterable, LazyBuffer, np.ndarray],
            *,
            device: ta.Optional[Device] = None,
            dtype: ta.Optional[Dtype] = None,
    ) -> 'Tensor':
        # if isinstance(data, list):
        #     data = np.array(data, dtype=(dtype if dtype is not None else Tensor.default_type).np)
        #
        # elif isinstance(data, LazyBuffer) and data.device != device:
        #     raise NotImplementedError
        #
        # if isinstance(data, np.ndarray):
        #     data = LazyNumpyArray(data, data.shape, data.dtype)
        #
        # if isinstance(data, LazyNumpyArray):
        #     if not data.shape:
        #         # FIXME: ??
        #         data = data.reshape(Shape(1,))
        #     lazydata = LazyBuffer.fromCPU(data.astype(dtype.np) if dtype is not None else data, device)
        # elif isinstance(data, LazyBuffer):
        #     assert dtype is None or dtype == data.dtype, "dtype doesn't match, and casting isn't supported"
        #     lazydata = data
        # else:
        #     raise RuntimeError(f"can't create Tensor from {data}")
        raise NotImplementedError

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
