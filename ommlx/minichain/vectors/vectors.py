"""
Storage:
 - f32 bytes
 - Sequence[float]
 - array.array
 - np.ndarray

Storage?:
 - memoryview ?
 - torch.Tensor ?
"""
import array
import typing as ta

from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import numpy as np
else:
    np = lang.proxy_import('numpy')


##


Vectorable: ta.TypeAlias = ta.Union[
    bytes,
    ta.Sequence[float],
    'array.array',
    'np.ndarray',
    'Vector',
]


class Vector(lang.Final):
    def __init__(self, obj: Vectorable) -> None:
        if isinstance(obj, Vector):
            check.is_(self, obj)
            return

        super().__init__()

        self._obj = obj

    def __new__(cls, obj):
        if isinstance(obj, Vector):
            return obj

        return super().__new__(cls)
