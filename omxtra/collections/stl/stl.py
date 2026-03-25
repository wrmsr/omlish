import collections.abc as cabc
import typing as ta

from . import _stl  # type: ignore


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class IntIntMap(_stl.MapI64I64, cabc.MutableMapping[int, int]):
    pass


class IntObjectMap(_stl.MapI64Obj, cabc.MutableMapping[int, V], ta.Generic[V]):
    pass


class ObjectIntMap(_stl.MapObjI64, cabc.MutableMapping[K, int], ta.Generic[K]):
    pass


class ObjectObjectMap(_stl.MapObjObj, cabc.MutableMapping[K, V], ta.Generic[K, V]):
    pass
