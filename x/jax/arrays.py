import typing as ta

import numpy as np

from . import prims
from .traces import Tracer
from .utils import swap


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
    _add = staticmethod(prims.add)
    _radd = staticmethod(swap(prims.add))
    _mul = staticmethod(prims.mul)
    _rmul = staticmethod(swap(prims.mul))
    _gt = staticmethod(prims.greater)
    _lt = staticmethod(prims.less)

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
    elif type(x) in prims.jax_types:
        return ConcreteArray(np.asarray(x))
    else:
        raise TypeError(x)


def zeros_like(val):
    aval = get_aval(val)
    return np.zeros(aval.shape, aval.dtype)


def mapped_aval(batch_dim, aval):
    shape = list(aval.shape)
    del shape[batch_dim]
    return ShapedArray(tuple(shape), aval.dtype)


def moveaxis(x, src: int, dst: int):
    perm = [i for i in range(np.ndim(x)) if i != src]
    perm.insert(dst, src)
    return prims.transpose(x, perm)
