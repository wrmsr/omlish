import abc
import typing as ta

from ... import lang


T = ta.TypeVar('T')
U = ta.TypeVar('U')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class SortedCollection(lang.Abstract, ta.Collection[T]):
    Comparator = ta.Callable[[U, U], int]

    @staticmethod
    def default_comparator(a: T, b: T) -> int:
        """https://docs.python.org/3.0/whatsnew/3.0.html#ordering-comparisons"""

        return (a > b) - (a < b)  # type: ignore

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def __contains__(self, value: T) -> bool:  # type: ignore
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, value: T) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def find(self, value: T) -> T | None:
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, value: T) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def iter(self, base: T | None = None) -> ta.Iterable[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def riter(self, base: T | None = None) -> ta.Iterable[T]:
        raise NotImplementedError


class SortedMapping(ta.Mapping[K, V]):
    @abc.abstractmethod
    def items(self) -> ta.Iterator[tuple[K, V]]:  # type: ignore
        raise NotImplementedError

    @abc.abstractmethod
    def ritems(self) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def itemsfrom(self, key: K) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def ritemsfrom(self, key: K) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError


class SortedMutableMapping(ta.MutableMapping[K, V], SortedMapping[K, V]):
    pass


class SortedListDict(SortedMutableMapping[K, V]):
    @staticmethod
    def _item_comparator(a: tuple[K, V], b: tuple[K, V]) -> int:
        return SortedCollection.default_comparator(a[0], b[0])

    def __init__(self, impl: SortedCollection, *args, **kwargs) -> None:
        super().__init__()
        self._impl = impl
        for k, v in lang.yield_dict_init(*args, **kwargs):
            self[k] = v

    @property
    def debug(self) -> ta.Mapping[K, V]:
        return dict(self)

    def __getitem__(self, key: K) -> V:
        item = self._impl.find((key, None))
        if item is None:
            raise KeyError(key)
        return item[1]

    def __setitem__(self, key: K, value: V) -> None:
        self._impl.remove((key, None))
        self._impl.add((key, value))

    def __delitem__(self, key: K) -> None:
        self._impl.remove((key, None))

    def __len__(self) -> int:
        return len(self._impl)

    def __iter__(self) -> ta.Iterator[K]:
        for k, _ in self._impl:
            yield k

    def items(self) -> ta.Iterator[tuple[K, V]]:  # type: ignore
        yield from self._impl.iter()

    def ritems(self) -> ta.Iterator[tuple[K, V]]:
        yield from self._impl.riter()

    def itemsfrom(self, key: K) -> ta.Iterator[tuple[K, V]]:
        yield from self._impl.iter((key, None))

    def ritemsfrom(self, key: K) -> ta.Iterator[tuple[K, V]]:
        yield from self._impl.riter((key, None))
