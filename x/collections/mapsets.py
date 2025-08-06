import typing as ta


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class MapSet(ta.AbstractSet[K], ta.Generic[K, V]):
    def __init__(self, dct: ta.Mapping[K, V]) -> None:
        super().__init__()

        self._dct = dct

    def __len__(self):
        return len(self._dct)

    def __iter__(self):
        return iter(self._dct)

    def __contains__(self, x):
        return x in self._dct

    def _hash(self) -> int:
        return hash(self._dct)

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


class MutableMapSet(MapSet[K, V], ta.MutableSet[K], ta.Generic[K, V]):
    def __init__(self, dct: ta.MutableMapping[K, V], default_value: V) -> None:
        super().__init__(dct)

        self._default_value = default_value

    _dct: ta.MutableMapping[K, V]

    def add(self, value):
        self._dct[value] = self._default_value

    def discard(self, value):
        try:
            del self._dct[value]
        except KeyError:
            pass

    def clear(self):
        self._dct.clear()

    def pop(self):
        raise NotImplementedError

    def remove(self, value):
        del self._dct[value]

    def __ior__(self, it):
        raise NotImplementedError

    def __iand__(self, it):
        raise NotImplementedError

    def __ixor__(self, it):
        raise NotImplementedError

    def __isub__(self, it):
        raise NotImplementedError
