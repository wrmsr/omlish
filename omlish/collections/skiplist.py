import random
import typing as ta

from .sorted import SortedCollection
from .sorted import SortedListDict


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


class SkipList(SortedCollection[T]):
    """https://gist.github.com/icejoywoo/3bf0c54983a725fa3917"""

    class _Node:
        __slots__ = [
            'value',
            'level',
            'next',
            'prev',
        ]

        next: list[ta.Optional['SkipList._Node']]
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
            node.prev = update[0]  # type: ignore

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


class SkipListDict(SortedListDict[K, V]):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(SkipList(comparator=SortedListDict._item_comparator), *args, **kwargs)
