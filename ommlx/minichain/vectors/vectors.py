"""
Preferred storage is array.array until numpy is imported.

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
import struct
import sys
import typing as ta

from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import numpy as np
else:
    np = lang.proxy_import('numpy')


_HAS_NP = lang.can_import('numpy')


##


VectorStorage: ta.TypeAlias = ta.Union[
    'array.array',
    'np.ndarray',
]


Vectorable: ta.TypeAlias = ta.Union[
    'Vector',
    'VectorStorage',
    bytes,
    ta.Sequence[float],
]


##


class _NdarrayPlaceholder(lang.NotInstantiable, lang.Final):
    pass


_Ndarray: type = _NdarrayPlaceholder


def _get_preferred_storage() -> type[VectorStorage]:
    if 'numpy' in sys.modules:
        global _Ndarray

        if _Ndarray is _NdarrayPlaceholder:
            _Ndarray = np.ndarray

        return np.ndarray

    else:
        return array.array


##


def _encode_float_bytes(fs: ta.Sequence[float]) -> bytes:
    return struct.pack('<' + 'f' * len(fs), *fs)


def _decode_float_bytes(b: bytes) -> ta.Sequence[float]:
    return struct.unpack('<' + 'f' * (len(b) // 4), b)


class Vector(lang.Final):
    def __init__(self, obj: Vectorable) -> None:
        if isinstance(obj, Vector):
            check.is_(self, obj)
            return

        super().__init__()

        self._storage = obj

    def __new__(cls, obj):
        if isinstance(obj, Vector):
            return obj

        return super().__new__(cls)
