import abc
import random
import typing as ta

from .. import lang
from .mappings import yield_dict_init


T = ta.TypeVar('T')
U = ta.TypeVar('U')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


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
    def find(self, value: T) -> ta.Optional[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, value: T) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def iter(self, base: ta.Optional[T] = None) -> ta.Iterable[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def riter(self, base: ta.Optional[T] = None) -> ta.Iterable[T]:
        raise NotImplementedError


class SkipList(SortedCollection[T]):
    """https://gist.github.com/icejoywoo/3bf0c54983a725fa3917"""

    class _Node:
        __slots__ = [
            'value',
            'level',
            'next',
            'prev',
        ]

        next: ta.List[ta.Optional['SkipList._Node']]
        prev: ta.Optional['SkipList._Node']

        def __init__(
                self,
                value: T,
                level: int
        ) -> None:
            super().__init__()

            if level <= 0:
                raise TypeError('level must be > 0')

            self.value = value
            self.level = level
            self.next = [None] * level
            self.prev = None

        def __repr__(self) -> str:
            return f'{type(self).__name__}(value={self.value!r})'

    def __init__(
            self,
            *,
            max_height: int = 16,
            comparator: ta.Optional[SortedCollection.Comparator[T]] = None,
    ) -> None:
        super().__init__()

        if comparator is None:
            comparator = SortedCollection.default_comparator
        self._compare = comparator
        self._max_height = max_height
        self._head = SkipList._Node(None, self._max_height)
        self._height = 1
        self._head.next = [None] * self._max_height
        self._length = 0

    def __len__(self) -> int:
        return self._length

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self.iter())

    def __contains__(self, value: T) -> bool:  # type: ignore
        return self.find(value) is not None

    def _random_level(self) -> int:
        result = 1
        while random.uniform(0, 1) < 0.5 and result < self._max_height:
            result += 1
        return result

    def add(self, value: T) -> bool:
        if value is None:
            raise TypeError(value)

        node = SkipList._Node(value, self._random_level())
        update = [None] * self._max_height  # noqa
        cur = self._head

        for i in range(self._height - 1, -1, -1):
            while cur.next[i] is not None and self._compare(value, cur.next[i].value) > 0:  # type: ignore
                cur = cur.next[i]  # type: ignore
            update[i] = cur  # type: ignore

        cur = cur.next[0]  # type: ignore
        if cur is not None:
            if self._compare(value, cur.value) == 0:  # type: ignore
                return False
            node.prev, cur.prev = cur.prev, node
        else:
            node.prev = update[0]

        if node.level > self._height:
            for i in range(self._height, node.level):
                update[i] = self._head  # type: ignore
            self._height = node.level

        for i in range(node.level):
            cur = update[i]  # type: ignore
            node.next[i] = cur.next[i]  # noqa
            cur.next[i] = node  # noqa

        self._length += 1
        return True

    def _find(self, value: T) -> ta.Optional[_Node]:
        if value is None:
            raise TypeError(value)

        cur = self._head

        for i in range(self._height - 1, -1, -1):
            while cur.next[i] and self._compare(value, cur.next[i].value) > 0:  # type: ignore
                cur = cur.next[i]  # type: ignore

        return cur.next[0]

    def find(self, value: T) -> ta.Optional[T]:
        node = self._find(value)
        if node is None:
            return None
        if node is None or self._compare(value, node.value) != 0:  # type: ignore
            return None
        return node.value  # type: ignore

    def remove(self, value: T) -> bool:
        if value is None:
            raise TypeError(value)

        update = [None] * self._max_height  # noqa
        cur = self._head

        for i in range(self._height - 1, -1, -1):
            while cur.next[i] is not None and self._compare(value, cur.next[i].value) > 0:  # type: ignore
                cur = cur.next[i]  # type: ignore
            update[i] = cur  # type: ignore

        cur = cur.next[0]  # type: ignore
        if cur is None or self._compare(value, cur.value) != 0:  # type: ignore
            return False
        elif cur.next[0] is not None:
            cur.next[0].prev = cur.prev

        for i in range(self._height):
            if update[i].next[i] is not cur:  # type: ignore
                break
            update[i].next[i] = cur.next[i]  # type: ignore

        while self._height > 0 and self._head.next[self._height - 1] is None:
            self._height -= 1

        self._length -= 1
        return True

    def iter(self, base: ta.Optional[T] = None) -> ta.Iterable[T]:
        if base is not None:
            cur = self._find(base)
            while cur is not None and self._compare(base, cur.value) > 0:  # type: ignore
                cur = cur.next[0]
        else:
            cur = self._head.next[0]

        while cur is not None:
            yield cur.value  # type: ignore
            cur = cur.next[0]

    def riter(self, base: ta.Optional[T] = None) -> ta.Iterable[T]:
        if base is not None:
            cur = self._find(base)
            while cur is not self._head and self._compare(base, cur.value) < 0:  # type: ignore
                cur = cur.prev  # type: ignore
        else:
            cur = self._head.next[self._height - 1]
            while True:
                next = cur.next[cur.next.index(None) - 1 if None in cur.next else -1]  # type: ignore  # noqa
                if next is None:
                    break
                cur = next

        while cur is not self._head:
            yield cur.value  # type: ignore
            cur = cur.prev  # type: ignore


class SortedMapping(ta.Mapping[K, V]):

    @abc.abstractmethod
    def items(self) -> ta.Iterator[ta.Tuple[K, V]]:  # type: ignore
        raise NotImplementedError

    @abc.abstractmethod
    def ritems(self) -> ta.Iterator[ta.Tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def itemsfrom(self, key: K) -> ta.Iterator[ta.Tuple[K, V]]:
        raise NotImplementedError

    @abc.abstractmethod
    def ritemsfrom(self, key: K) -> ta.Iterator[ta.Tuple[K, V]]:
        raise NotImplementedError


class SortedMutableMapping(ta.MutableMapping[K, V], SortedMapping[K, V]):
    pass


class SortedListDict(SortedMutableMapping[K, V]):

    @staticmethod
    def _item_comparator(a: ta.Tuple[K, V], b: ta.Tuple[K, V]) -> int:
        return SortedCollection.default_comparator(a[0], b[0])

    def __init__(self, impl: SortedCollection, *args, **kwargs) -> None:
        super().__init__()
        self._impl = impl
        for k, v in yield_dict_init(*args, **kwargs):
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
        for k, v in self._impl:
            yield k

    def items(self) -> ta.Iterator[ta.Tuple[K, V]]:  # type: ignore
        yield from self._impl.iter()  # type: ignore

    def ritems(self) -> ta.Iterator[ta.Tuple[K, V]]:
        yield from self._impl.riter()

    def itemsfrom(self, key: K) -> ta.Iterator[ta.Tuple[K, V]]:
        yield from self._impl.iter((key, None))

    def ritemsfrom(self, key: K) -> ta.Iterator[ta.Tuple[K, V]]:
        yield from self._impl.riter((key, None))


class SkipListDict(SortedListDict[K, V]):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(SkipList(comparator=SortedListDict._item_comparator), *args, **kwargs)
