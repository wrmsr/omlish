import abc
import typing as ta

from omlish import check
from omlish import defs
from omlish import lang
import numpy as np

from .dtypes import Dtype
from .numpy import NUMPY_VALUE_TYPES
from .numpy import NumpyValue


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
    def to_cpu(self) -> NumpyValue:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_cpu(cls: ta.Type[T], x: NumpyValue) -> T:
        raise NotImplementedError


class RawConst(RawBuffer, lang.Final):
    def __init__(self, x: np.number) -> None:
        check.isinstance(x, np.number)
        super().__init__(1, Dtype.of_np(x.dtype))
        self._x = x

    def to_cpu(self) -> NumpyValue:
        return self._x

    @classmethod
    def from_cpu(cls, x: NumpyValue) -> 'RawConst':
        return RawConst(x.item())


class RawCpuBuffer(RawBuffer):
    def __init__(self, buf: NumpyValue) -> None:
        check.isinstance(buf, NUMPY_VALUE_TYPES)
        super().__init__(buf.size, Dtype.of_np(buf.dtype))
        self._buf = buf

    def to_cpu(self) -> NumpyValue:
        return self._buf

    @classmethod
    def from_cpu(cls: ta.Type[T], x: NumpyValue) -> T:
        return cls(x)  # type: ignore
