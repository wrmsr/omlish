import typing as ta

import numpy as np

from .scalars import SCALAR_TYPES
from .scalars import Scalar


NumpyValue = ta.Union[np.ndarray, np.generic]

NUMPY_VALUE_TYPES = (np.ndarray, np.generic)


def np_to_scalar(v: ta.Union[np.number, Scalar]) -> Scalar:
    if isinstance(v, np.floating):
        return float(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, SCALAR_TYPES):
        return v
    raise TypeError(v)
