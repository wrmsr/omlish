import abc
import collections.abc
import itertools
import typing as ta

from .. import lang


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


class Frozen(ta.Hashable, abc.ABC):
    pass


class FrozenDict(ta.Mapping[K, V], Frozen):
    def __new__(cls, *args: ta.Any, **kwargs: ta.Any) -> 'FrozenDict[K, V]':  # noqa
        if len(args) == 1 and Frozen in type(args[0]).__bases__:
            return args[0]
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._hash = None
        if len(args) > 1:
            raise TypeError(args)
        self._dct: dict[K, V] = {}
        self._dct.update(lang.yield_dict_init(*args, **kwargs))

    @property
    def debug(self) -> ta.Mapping[K, V]:
        return dict(self._dct)

    def __repr__(self) -> str:
        return f'({self._dct!r})'

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and self._dct == other._dct

    def __getitem__(self, key: K) -> V:
        return self._dct[key]

    def __getstate__(self):
        return tuple(self.items())

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(tuple((k, self[k]) for k in sorted(self)))  # type: ignore
        return self._hash

    def __iter__(self) -> ta.Iterator[K]:
        return iter(self._dct)

    def __len__(self) -> int:
        return len(self._dct)

    def __ne__(self, other) -> bool:
        return not (self == other)

    def __setstate__(self, t):
        self.__init__(t)  # type: ignore

    def drop(self, *keys: T) -> 'FrozenDict[K, V]':
        ks = frozenset(keys)
        return type(self)((k, self[k]) for k in self if k not in ks)

    def set(self, *args: ta.Any, **kwargs: ta.Any) -> 'FrozenDict[K, V]':
        new = type(self)(*args, **kwargs)
        return type(self)(itertools.chain(self.items(), new.items()))


class FrozenList(ta.Sequence[T], Frozen):
    def __init__(self, it: ta.Iterable[T] | None = None) -> None:
        super().__init__()

        self._tup: tuple = tuple(it) if it is not None else ()
        self._hash: int | None = None

    @property
    def debug(self) -> ta.Sequence[T]:
        return list(self)

    def __repr__(self) -> str:
        return f'([{", ".join(map(repr, self._tup))}])'

    def __add__(self, o) -> 'FrozenList[T]':
        if isinstance(o, FrozenList):
            return FrozenList(self._tup + o._tup)
        elif isinstance(o, collections.abc.Sequence):
            return FrozenList(self._tup + tuple(o))
        else:
            return NotImplemented

    def __contains__(self, x: object) -> bool:
        return x in self._tup

    def __eq__(self, o: object) -> bool:
        if isinstance(o, FrozenList):
            return self._tup == o._tup
        elif isinstance(o, collections.abc.Sequence):
            return len(self) == len(o) and all(l == r for l, r in zip(self, o))
        else:
            return False

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self._tup)
        return self._hash

    def __getitem__(self, idx: int | slice) -> 'FrozenList[T]':  # type: ignore
        if isinstance(idx, int):
            return self._tup[idx]
        else:
            return FrozenList(self._tup[idx])

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._tup)

    def __len__(self) -> int:
        return len(self._tup)

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __radd__(self, o) -> 'FrozenList[T]':
        if isinstance(o, FrozenList):
            return FrozenList(o._tup + self._tup)
        elif isinstance(o, collections.abc.Sequence):
            return FrozenList(tuple(o) + self._tup)
        else:
            return NotImplemented

    def __reversed__(self) -> ta.Iterator[T]:
        return reversed(self._tup)

    def count(self, x: ta.Any) -> int:
        return super().count(x)

    def index(self, x: ta.Any, *args, **kwargs) -> int:  # type: ignore
        return self._tup.index(x, *args, **kwargs)


frozendict = FrozenDict
frozenlist = FrozenList
