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
