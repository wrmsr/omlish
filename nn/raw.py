import abc
import typing as ta

from omlish import check
from omlish import defs
from omlish import lang
import numpy as np

from .dtypes import Dtype


T = ta.TypeVar('T')


class RawBuffer(lang.Abstract):
    def __init__(self, sz: int, dt: Dtype) -> None:
        super().__init__()

        self._sz = check.isinstance(sz, int)
        self._dt = check.isinstance(dt, Dtype)

    defs.repr('size', 'dtype')

    @property
    def size(self) -> int:
        return self._sz

    @property
    def dtype(self) -> Dtype:
        return self._dt

    @abc.abstractmethod
    def to_cpu(self) -> np.ndarray:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_cpu(cls: ta.Type[T], x: np.ndarray) -> T:
        raise NotImplementedError


class RawConst(RawBuffer, lang.Final):
    def __init__(self, x: np.number) -> None:
        check.isinstance(x, np.number)
        super().__init__(1, Dtype.of_np(x.dtype))
        self._x = x

    def to_cpu(self) -> np.ndarray:
        return np.asarray(self._x)

    @classmethod
    def from_cpu(cls, x: np.ndarray) -> 'RawConst':
        check.arg(x.shape == (1,))
        return RawConst(x[0])
