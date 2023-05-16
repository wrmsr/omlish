import typing as ta

from omlish import dataclasses as dc
import numpy as np

from .dims import Shape
from .dtypes import Dtype


@dc.dataclass(frozen=True)
class LazyNpArray:
    src: ta.Any  # np.array_like | Callable[[LazyNpArray], np.array_like]
    shape: Shape
    dtype: Dtype = dc.field(check=lambda v: isinstance(v, Dtype))

    def __call__(self) -> np.ndarray:
        return np.require(
            self.src(self) if callable(self.src) else self.src,
            dtype=self.dtype.np,
            requirements='C',
        ).reshape(self.shape)

    def reshape(self, shape: Shape) -> 'LazyNpArray':
        return dc.replace(self, shape=shape)

    def astype(self, dtype: Dtype) -> 'LazyNpArray':
        return dc.replace(self, dtype=dtype)
