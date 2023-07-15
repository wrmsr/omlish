import abc
import math
import typing as ta

from omlish import check
from omlish import defs
from omlish import lang
import numpy as np

from .dtypes import Dtype
from .dtypes import SCALAR_TYPES
from .dtypes import Scalar
from .numpy import NUMPY_VALUE_TYPES
from .numpy import NumpyValue


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
    def from_cpu(cls, x: NumpyValue) -> 'RawBuffer':
        raise NotImplementedError


class RawConst(RawBuffer, lang.Final):
    def __init__(self, x: Scalar, dtype: Dtype) -> None:
        check.isinstance(x, SCALAR_TYPES)
        super().__init__(1, dtype)
        self._x = x

    def to_cpu(self) -> NumpyValue:
        return self._x

    @classmethod
    def from_cpu(cls, x: NumpyValue) -> RawBuffer:
        return RawConst(x.item())


class RawCpuBuffer(RawBuffer):
    def __init__(self, buf: NumpyValue) -> None:
        check.isinstance(buf, NUMPY_VALUE_TYPES)
        super().__init__(buf.size, Dtype.of_np(buf.dtype))
        self._buf = buf

    def to_cpu(self) -> NumpyValue:
        return self._buf

    @classmethod
    def from_cpu(cls, x: NumpyValue) -> RawBuffer:
        return cls(x)


class RawBufferCopyIn(RawBuffer, lang.Abstract):

    @abc.abstractmethod
    def _copy_in(self, x: NumpyValue) -> None:
        raise NotImplementedError

    @classmethod
    def from_cpu(cls, x: NumpyValue, **kwargs: ta.Any) -> RawBuffer:
        ret = cls(math.prod(x.shape), Dtype.of_np(x.dtype), **kwargs)
        ret._copy_in(x)
        return ret


class RawBufferMapped(RawBufferCopyIn, lang.Abstract):

    @abc.abstractmethod
    def _buffer(self) -> memoryview:
        raise NotImplementedError

    def to_cpu(self) -> NumpyValue:
        return np.frombuffer(self._buffer(), dtype=self.dtype.np)

    def _copy_in(self, x: NumpyValue) -> None:
        np.copyto(check.isinstance(self.to_cpu(), np.ndarray), x.reshape(-1))


class RawBufferCopyInOut(RawBufferCopyIn, lang.Abstract):  # noqa

    def _copy_out(self, x: NumpyValue) -> None:
        raise NotImplementedError

    def to_cpu(self) -> NumpyValue:
        x: np.ndarray = np.empty(self.size, dtype=self.dtype.np)
        self._copy_out(x)
        return x
