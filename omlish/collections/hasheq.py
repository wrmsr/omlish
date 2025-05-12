"""
TODO:
 - order preserving / linked list?
 - ItemsView
"""
import abc
import dataclasses as dc
import typing as ta

from .. import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')
K2 = ta.TypeVar('K2')
V2 = ta.TypeVar('V2')


##


class HashEq(lang.Abstract, ta.Generic[K]):
    @abc.abstractmethod
    def hash(self, k: K) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def eq(self, l: K, r: K) -> bool:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class HashEq_(ta.Generic[K]):  # noqa
    hash: ta.Callable[[K], int]
    eq: ta.Callable[[K, K], bool]


class hash_eq(HashEq[K], lang.NotInstantiable, lang.Final):  # noqa
    """Workaround for PEP 695 support."""

    def __new__(  # type: ignore[misc]
            cls,
            hash: ta.Callable[[K], int],  # noqa
            eq: ta.Callable[[K, K], bool],
    ) -> HashEq[K]:
        return HashEq_(hash, eq)  # type: ignore

    def hash(self, k: K) -> int:
        raise TypeError

    def eq(self, l: K, r: K) -> bool:
        raise TypeError


class HashEqMap(ta.MutableMapping[K, V]):
    class _Node(ta.NamedTuple, ta.Generic[K2, V2]):
        k: K2
        v: V2
        h: int

    def __init__(self, hash_eq: HashEq[K], *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()

        self._hash_eq = hash_eq

        self._dct: dict[int, list[HashEqMap._Node[K, V]]] = {}
        self._len = 0

        for k, v in lang.yield_dict_init(*args, **kwargs):
            self[k] = v

    def __len__(self) -> int:
        return self._len

    def clear(self) -> None:
        self._dct.clear()
        self._len = 0

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
                if not l:
                    del self._dct[h]
                self._len -= 1
                return
        raise KeyError(k)

    def __iter__(self) -> ta.Iterator[K]:
        return self.iterkeys()

    def iterkeys(self) -> ta.Iterator[K]:
        for l in self._dct.values():
            for e in l:
                yield e.k

    def itervalues(self) -> ta.Iterator[V]:
        for l in self._dct.values():
            for e in l:
                yield e.v

    def iteritems(self) -> ta.Iterator[tuple[K, V]]:
        for l in self._dct.values():
            for e in l:
                yield (e.k, e.v)

    # FIXME:

    def keys(self) -> ta.Iterable[K]:  # type: ignore[override]
        return lang.itergen(self.iterkeys)

    def values(self) -> ta.Iterable[V]:  # type: ignore[override]
        return lang.itergen(self.itervalues)

    def items(self) -> ta.Iterable[tuple[K, V]]:  # type: ignore[override]
        return lang.itergen(self.iteritems)
