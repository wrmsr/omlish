import operator as op
import typing as ta
import weakref

from .. import lang


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class IdentityKeyDict(ta.MutableMapping[K, V]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        self._dict: dict[int, tuple[K, V]] = {}
        for k, v in lang.yield_dict_init(*args, **kwargs):
            self[k] = v

    def __reduce__(self):
        return (type(self), (list(self.items()),))

    @property
    def debug(self) -> ta.Sequence[tuple[K, V]]:
        return list(self.items())

    def __repr__(self) -> str:
        return lang.attr_repr(self, '_dict')

    def __setitem__(self, k: K, v: V) -> None:
        self._dict[id(k)] = (k, v)

    def __delitem__(self, k: K) -> None:
        del self._dict[id(k)]

    def __getitem__(self, k: K) -> V:
        return self._dict[id(k)][1]

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> ta.Iterator[K]:
        return iter(map(op.itemgetter(0), self._dict.values()))

    def clear(self) -> None:
        self._dict.clear()


class IdentitySet(ta.MutableSet[T]):
    def __init__(self, init: ta.Iterable[T] | None = None) -> None:
        super().__init__()

        self._dict: dict[int, T] = {}
        if init is not None:
            for item in init:
                self.add(item)

    def __reduce__(self):
        return (type(self), (list(self),))

    @property
    def debug(self) -> ta.Sequence[T]:
        return list(self)

    def __repr__(self) -> str:
        return lang.attr_repr(self, '_dict')

    def add(self, item: T) -> None:
        self._dict[id(item)] = item

    def discard(self, item: T) -> None:
        try:
            del self._dict[id(item)]
        except KeyError:
            pass

    def update(self, items: ta.Iterable[T]) -> None:
        for item in items:
            self.add(item)

    def __contains__(self, item: T) -> bool:  # type: ignore
        return id(item) in self._dict

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._dict.values())


##


class IdentityWeakKeyDictionary(ta.MutableMapping[K, V]):
    """
    https://ideone.com/G4iIri
    https://stackoverflow.com/questions/75314250/python-weakkeydictionary-for-unhashable-types#comment135919973_77100606

    See also:
    https://github.com/python-trio/trio/blob/efd785a20721707b52a6e2289a65e25722b30c96/src/trio/_core/_ki.py#L81

    TODO:
     - audit for freethreaded
      - leans on stdlib impls so shouldn't matter?
    """

    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()

        self._keys: ta.MutableMapping[IdentityWeakKeyDictionary._Id[K], K] = weakref.WeakValueDictionary()
        self._values: ta.MutableMapping[IdentityWeakKeyDictionary._Id[K], V] = weakref.WeakKeyDictionary()

        for k, v in lang.yield_dict_init(*args, **kwargs):
            self[k] = v

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> ta.Iterator[K]:
        return iter(self._keys.values())

    class _Id(ta.Generic[T]):
        def __init__(self, key: T) -> None:
            super().__init__()

            self._id = id(key)
            self._key_ref = weakref.ref(key)

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}<id={self._id}>'

        def __hash__(self) -> int:
            return self._id

        def __eq__(self, other: object) -> bool:
            return (
                type(other) is type(self) and
                self._id == other._id and  # type: ignore  # noqa
                self._key_ref() is other._key_ref()  # type: ignore  # noqa
            )

        def __ne__(self, other: object) -> bool:
            return not (self == other)

    def __getitem__(self, key: K) -> V:
        return self._values.__getitem__(self._Id(key))

    def __setitem__(self, key: K, value: V) -> None:
        id_obj = self._Id(key)
        self._keys.__setitem__(id_obj, key)
        self._values.__setitem__(id_obj, value)

    def __delitem__(self, key: K) -> None:
        self._values.__delitem__(self._Id(key))
        self._keys.__delitem__(self._Id(key))


class IdentityWeakSet(ta.MutableSet[T]):
    def __init__(self, init: ta.Iterable[T] | None = None) -> None:
        super().__init__()

        self._dict: IdentityWeakKeyDictionary[T, None] = IdentityWeakKeyDictionary()

        if init is not None:
            for e in init:
                self._dict[e] = None

    def add(self, value):
        self._dict[value] = None

    def discard(self, value):
        del self._dict[value]

    def __contains__(self, x):
        return x in self._dict

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return self._dict.keys()
