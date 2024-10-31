"""
TODO:
 - order preserving / linked list?
"""
import typing as ta


K = ta.TypeVar('K')
V = ta.TypeVar('V')
K2 = ta.TypeVar('K2')
V2 = ta.TypeVar('V2')
K_co = ta.TypeVar('K_co', covariant=True)


class HashEq(ta.Protocol[K_co]):
    def hash(self, k: K) -> int: ...
    def eq(self, l: K, r: K) -> bool: ...


class HashEqMap(ta.Mapping[K, V]):
    class _Node(ta.NamedTuple, ta.Generic[K2, V2]):
        k: K2
        v: V2
        h: int

    def __init__(self, hash_eq: HashEq[K]) -> None:
        super().__init__()
        self._hash_eq = hash_eq
        self._dct: dict[int, list[HashEqMap._Node[K, V]]] = {}
        self._len = 0

    def __len__(self) -> int:
        return self._len

    def __contains__(self, k: K) -> bool:  # type: ignore[override]
        h = self._hash_eq.hash(k)
        try:
            l = self._dct[h]
        except KeyError:
            return False
        return any(self._hash_eq.eq(k, e.k) for e in l)

    def __getitem__(self, k: K) -> V:
        h = self._hash_eq.hash(k)
        l = self._dct[h]
        for e in l:
            if self._hash_eq.eq(k, e.k):
                return e.v
        raise KeyError(k)

    def __setitem__(self, k: K, v: V) -> None:
        h = self._hash_eq.hash(k)
        n = HashEqMap._Node(k, v, h)

        try:
            l = self._dct[h]
        except KeyError:
            l = [n]
            self._dct[h] = l
            self._len += 1
            return

        for i, e in enumerate(l):
            if self._hash_eq.eq(k, e.k):
                l[i] = n
                return

        l.append(n)
        self._len += 1

    def __delitem__(self, k: K) -> None:
        h = self._hash_eq.hash(k)
        l = self._dct[h]
        for i, e in enumerate(l):
            if self._hash_eq.eq(k, e.k):
                del l[i]
                self._len -= 1
                return
        raise KeyError(k)
