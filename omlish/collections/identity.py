import operator as op
import typing as ta
import weakref

from .. import lang


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class IdentityWrapper(ta.Generic[T]):
    def __init__(self, value: T) -> None:
        super().__init__()

        self._value = value

    def __repr__(self) -> str:
        return lang.attr_repr(self, 'value')

    @property
    def value(self) -> T:
        return self._value

    def __eq__(self, other):
        return isinstance(other, IdentityWrapper) and other._value is self._value

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return id(self._value)


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


class IdentityWeakSet(ta.MutableSet[T]):
    def __init__(self, init: ta.Iterable[T] | None = None) -> None:
        super().__init__()

        self._dict: weakref.WeakValueDictionary[int, T] = weakref.WeakValueDictionary()

    def add(self, value):
        # FIXME: race with weakref callback?
        self._dict[id(value)] = value

    def discard(self, value):
        try:
            del self._dict[id(value)]
        except KeyError:
            pass

    def __contains__(self, x):
        try:
            o = self._dict[id(x)]
        except KeyError:
            return False
        return x is o

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return self._dict.values()
