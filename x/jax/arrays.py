import typing as ta

import numpy as np

from . import prims
from .traces import Tracer


class ShapedArray:
    array_abstraction_level = 1
    shape: ta.Tuple[int, ...]
    dtype: np.dtype

    def __init__(self, shape, dtype):
        self.shape = shape
        self.dtype = dtype

    @property
    def ndim(self):
        return len(self.shape)

    _neg = staticmethod(prims.neg)
    _add = staticmethod(add)
    _radd = staticmethod(swap(add))
    _mul = staticmethod(mul)
    _rmul = staticmethod(swap(mul))
    _gt = staticmethod(greater)
    _lt = staticmethod(less)

    @staticmethod
    def _bool(tracer):
        raise Exception("ShapedArray can't be unambiguously converted to bool")

    @staticmethod
    def _nonzero(tracer):
        raise Exception("ShapedArray can't be unambiguously converted to bool")

    def str_short(self):
        return f'{self.dtype.name}[{",".join(str(d) for d in self.shape)}]'

    def __hash__(self):
        return hash((self.shape, self.dtype))

    def __eq__(self, other):
        return (
                type(self) is type(other) and
                self.shape == other.shape and
                self.dtype == other.dtype
        )

    def __repr__(self):
        return f"ShapedArray(shape={self.shape}, dtype={self.dtype})"


class ConcreteArray(ShapedArray):
    array_abstraction_level = 2
    val: np.ndarray

    def __init__(self, val):
        super().__init__(val.shape, val.dtype)
        self.val = val

    @staticmethod
    def _bool(tracer):
        return bool(tracer.aval.val)

    @staticmethod
    def _nonzero(tracer):
        return bool(tracer.aval.val)


def get_aval(x):
    if isinstance(x, Tracer):
        return x.aval
    elif type(x) in jax_types:
        return ConcreteArray(np.asarray(x))
    else:
        raise TypeError(x)


jax_types = {
    bool,
    int,
    float,
    np.bool_,
    np.int32,
    np.int64,
    np.float32,
    np.float64,
    np.ndarray,
}
