import typing as ta
from typing import Iterable
from typing import MutableMapping
from typing import overload

T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class ContextManagedMapping(ta.Mapping[K, V]):
    def __init__(self, dct: ta.Mapping[K, V]) -> None:
        super().__init__()

        self._dct = dct

    def __getitem__(self, key, /):
        raise NotImplementedError

    @ta.overload
    def get(self, key: K, /) -> V | None:
        ...

    @ta.overload
    def get(self, key: K, /, default: V | T) -> V | T:
        ...

    def get(self, key, /):
        raise NotImplementedError

    def items(self):
        raise NotImplementedError

    def keys(self):
        raise NotImplementedError

    def values(self):
        raise NotImplementedError

    def __contains__(self, key, /):
        raise NotImplementedError

    def __eq__(self, other, /):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


class SupportsKeysAndGetItem(ta.Protocol[K, V]):
    def keys(self) -> Iterable[K]:
        ...

    def __getitem__(self, key: K, /) -> V:
        ...


class ContextManagedMutableMapping(ContextManagedMapping[K, V], ta.MutableMapping[K, V]):
    def __init__(self, dct: ta.MutableMapping[K, V]) -> None:
        super().__init__(dct)

    _dct: ta.MutableMapping[K, V]

    def __setitem__(self, key, value, /):
        raise NotImplementedError

    def __delitem__(self, key, /):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    @overload
    def pop(self, key: K, /) -> V: ...

    @overload
    def pop(self, key: K, /, default: V) -> V: ...

    @overload
    def pop(self, key: K, /, default: T) -> V | T: ...

    def pop(self, key, /):
        raise NotImplementedError

    def popitem(self):
        raise NotImplementedError

    @overload
    def setdefault(self: MutableMapping[K, T | None], key: K, default: None = None, /) -> T | None:
        ...

    @overload
    def setdefault(self, key: K, default: V, /) -> V:
        ...

    def setdefault(self, key, default=None, /):
        raise NotImplementedError

    @overload
    def update(self, m: SupportsKeysAndGetItem[K, V], /, **kwargs: V) -> None: ...

    @overload
    def update(self, m: Iterable[tuple[K, V]], /, **kwargs: V) -> None: ...

    @overload
    def update(self, **kwargs: V) -> None: ...

    def update(self, m, /, **kwargs):
        raise NotImplementedError


class ContextManagedSet(ta.AbstractSet[T]):
    def __init__(self, dct: ta.AbstractSet[T]) -> None:
        super().__init__()

        self._dct = dct

    def __contains__(self, x):
        raise NotImplementedError

    def _hash(self):
        raise NotImplementedError

    def __le__(self, other):
        raise NotImplementedError

    def __lt__(self, other):
        raise NotImplementedError

    def __gt__(self, other):
        raise NotImplementedError

    def __ge__(self, other):
        raise NotImplementedError

    def __and__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __sub__(self, other):
        raise NotImplementedError

    def __xor__(self, other):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def isdisjoint(self, other):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


class ContextManagedMutableSet(ContextManagedSet[T], ta.MutableSet[T]):
    def add(self, value):
        raise NotImplementedError

    def discard(self, value):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

    def remove(self, value):
        raise NotImplementedError

    def __ior__(self, it):
        raise NotImplementedError

    def __iand__(self, it):
        raise NotImplementedError

    def __ixor__(self, it):
        raise NotImplementedError

    def __isub__(self, it):
        raise NotImplementedError