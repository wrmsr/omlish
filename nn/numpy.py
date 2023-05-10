import typing as ta

from omlish import dataclasses as dc
import numpy as np

from .dims import Shape
from .dtypes import Dtype


@dc.dataclass(frozen=True)
class LazyNumpyArray:
    src: ta.Any  # np.array_like | Callable[[LazyNumpyArray], np.array_like]
    shape: Shape
    dtype: Dtype

    def __call__(self) -> np.ndarray:
        return np.require(
            self.src(self) if callable(self.src) else self.src,
            dtype=self.dtype.numpy,
            requirements='C',
        ).reshape(self.shape)

    def reshape(self, shape: Shape) -> 'LazyNumpyArray':
        return dc.replace(self, shape=shape)

    def astype(self, dtype: Dtype) -> 'LazyNumpyArray':
        return dc.replace(self, dtype=dtype)
