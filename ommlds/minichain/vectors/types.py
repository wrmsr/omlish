"""
TODO:
 - marshal
 - __getitem__ return Vector? views? this isn't a replacement for strided tensors, just List[float]
 - memoryview?
 - torch.Tensor?
"""
import array
import functools
import struct
import sys
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


if ta.TYPE_CHECKING:
    import numpy as np
else:
    np = lang.proxy_import('numpy')


msh.register_global_module_import('._marshal', __package__)


##


VectorStorage: ta.TypeAlias = ta.Union[
    array.array,
    'np.ndarray',
]


Vectorable: ta.TypeAlias = ta.Union[
    'Vector',
    'VectorStorage',
    bytes,
    ta.Iterable[float],
]


##


@dc.dataclass(frozen=True)
class _StorageImpl:
    cls: type[VectorStorage]
    ctor: ta.Callable[[ta.Iterable[float]], VectorStorage]

    _: dc.KW_ONLY

    is_np: bool = False


_ARRAY_STORAGE_IMPL = _StorageImpl(
    array.array,
    functools.partial(array.array, 'f'),
)

_STORAGE_IMPL: _StorageImpl = _ARRAY_STORAGE_IMPL


def _get_storage_impl() -> _StorageImpl:
    if 'numpy' in sys.modules:
        global _STORAGE_IMPL

        if _STORAGE_IMPL is _ARRAY_STORAGE_IMPL:
            _STORAGE_IMPL = _StorageImpl(
                np.ndarray,
                functools.partial(np.array, dtype=np.float32),
                is_np=True,
            )

    return _STORAGE_IMPL  # noqa


##


_STRUCT_FLOATS_FMTS: dict[int, str] = {}


def _get_struct_float_fmt(d: int) -> str:
    try:
        return _STRUCT_FLOATS_FMTS[d]
    except KeyError:
        fmt = _STRUCT_FLOATS_FMTS[d] = '<' + 'f' * d
        return fmt


def _encode_float_bytes(fs: ta.Sequence[float]) -> bytes:
    return struct.pack(_get_struct_float_fmt(len(fs)), *fs)


def _decode_float_bytes(b: bytes) -> ta.Sequence[float]:
    return struct.unpack(_get_struct_float_fmt(len(b) // 4), b)


##


class Vector(lang.Final, ta.Sequence[float]):
    def __init__(self, obj: Vectorable) -> None:
        if isinstance(obj, Vector):
            check.is_(self, obj)
            return

        super().__init__()

        s: VectorStorage
        si = _get_storage_impl()
        if isinstance(obj, si.cls):
            s = obj  # type: ignore
        else:
            l: ta.Iterable[float]
            if isinstance(obj, bytes):
                l = _decode_float_bytes(obj)
            else:
                l = obj
            s = si.ctor(l)

        self._s = s

    def __new__(cls, obj):
        if isinstance(obj, Vector):
            return obj

        return super().__new__(cls)

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}<{self._s!r}>'

    #

    def __iter__(self) -> ta.Iterator[float]:
        return iter(self._s)

    @ta.overload
    def __getitem__(self, index: int) -> float:
        ...

    @ta.overload
    def __getitem__(self, index: slice) -> ta.Sequence[float]:
        ...

    def __getitem__(self, index):
        return self._s[index]

    def __len__(self) -> int:
        return len(self._s)

    #

    def bytes(self) -> bytes:
        return _encode_float_bytes(self._s)  # type: ignore

    def np(self) -> 'np.ndarray':
        si = _get_storage_impl()

        if not si.is_np:
            import numpy  # noqa

            si = _get_storage_impl()
            check.state(si.is_np)

        if not isinstance(self._s, si.cls):
            self._s = si.ctor(self._s)

        return self._s  # type: ignore
