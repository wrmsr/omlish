import abc
import typing as ta

from ... import lang


T = ta.TypeVar('T')
U = ta.TypeVar('U')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class SortedIter(lang.Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def iter(self) -> ta.Iterator[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def iter_desc(self) -> ta.Iterator[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def iter_from(self, base: T) -> ta.Iterator[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def iter_from_desc(self, base: T) -> ta.Iterator[T]:
        raise NotImplementedError


class SortedCollection(
    SortedIter[T],
    ta.Collection[T],
    lang.Abstract,
    ta.Generic[T],
):
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


#


class SortedItems(lang.Abstract, ta.Generic[K, V]):
    @abc.abstractmethod
    def items(self) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def items_desc(self) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def items_from(self, key: K) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def items_from_desc(self, key: K) -> ta.Iterator[tuple[K, V]]:
        raise NotImplementedError


class SortedMapping(
    SortedItems[K, V],
    ta.Mapping[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    @abc.abstractmethod
    def items(self) -> ta.Iterator[tuple[K, V]]:  # type: ignore[override]  # FIXME: ItemsView
        raise NotImplementedError


class SortedMutableMapping(
    ta.MutableMapping[K, V],
    SortedMapping[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass


##


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

    def items_desc(self) -> ta.Iterator[tuple[K, V]]:
        yield from self._impl.iter_desc()

    def items_from(self, key: K) -> ta.Iterator[tuple[K, V]]:
        yield from self._impl.iter_from((key, None))

    def items_from_desc(self, key: K) -> ta.Iterator[tuple[K, V]]:
        yield from self._impl.iter_from_desc((key, None))
