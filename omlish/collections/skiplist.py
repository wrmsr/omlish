import random
import typing as ta

from .sorted import SortedCollection
from .sorted import SortedListDict


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


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
                level: int,
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
            comparator: SortedCollection.Comparator[T] | None = None,
    ) -> None:
        super().__init__()

        if comparator is None:
            comparator = SortedCollection.default_comparator
        self._compare = comparator
        self._max_height = max_height

        self._head = SkipList._Node(None, self._max_height)
        self._tail = self._head
        self._height = 1
        self._length = 0

    #

    def __len__(self) -> int:
        return self._length

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self.iter())

    def __contains__(self, value: T) -> bool:  # type: ignore
        return self.find(value) is not None

    #

    def _random_level(self) -> int:
        result = 1
        while random.uniform(0, 1) < 0.5 and result < self._max_height:
            result += 1
        return result

    def add(self, value: T) -> bool:
        if value is None:
            raise TypeError(value)

        # Pre-fill update with head to handle height increases safely
        update = [self._head] * self._max_height
        cur = self._head

        for i in range(self._height - 1, -1, -1):
            while cur.next[i] is not None and self._compare(value, cur.next[i].value) > 0:  # type: ignore
                cur = cur.next[i]  # type: ignore
            update[i] = cur

        target = cur.next[0]
        if target is not None and self._compare(value, target.value) == 0:  # type: ignore
            return False

        node = SkipList._Node(value, self._random_level())

        if node.level > self._height:
            self._height = node.level

        for i in range(node.level):
            node.next[i] = update[i].next[i]
            update[i].next[i] = node

        # Correctly wire up the doubly-linked list layer (Level 0)
        node.prev = update[0]
        if node.next[0] is not None:
            node.next[0].prev = node
        else:
            self._tail = node  # New node is at the end

        self._length += 1
        return True

    #

    def _find(self, value: T) -> _Node | None:
        if value is None:
            raise TypeError(value)

        cur = self._head

        for i in range(self._height - 1, -1, -1):
            while cur.next[i] and self._compare(value, cur.next[i].value) > 0:  # type: ignore
                cur = cur.next[i]  # type: ignore

        return cur.next[0]

    def find(self, value: T) -> T | None:
        node = self._find(value)
        if node is None:
            return None
        if node is None or self._compare(value, node.value) != 0:  # type: ignore
            return None
        return node.value  # type: ignore

    #

    def remove(self, value: T) -> bool:
        if value is None:
            raise TypeError(value)

        update = [None] * self._max_height
        cur = self._head

        for i in range(self._height - 1, -1, -1):
            while cur.next[i] is not None and self._compare(value, cur.next[i].value) > 0:  # type: ignore
                cur = cur.next[i]  # type: ignore
            update[i] = cur  # type: ignore

        target = cur.next[0]
        if target is None or self._compare(value, target.value) != 0:  # type: ignore
            return False

        # Update next pointers and height
        for i in range(self._height):
            if update[i].next[i] is not target:  # type: ignore
                break
            update[i].next[i] = target.next[i]  # type: ignore

        # Correctly update prev pointer and tail
        if target.next[0] is not None:
            target.next[0].prev = target.prev
        else:
            self._tail = target.prev  # type: ignore

        while self._height > 1 and self._head.next[self._height - 1] is None:
            self._height -= 1

        self._length -= 1
        return True

    #

    def iter(self) -> ta.Iterator[T]:
        cur = self._head.next[0]

        while cur is not None:
            yield cur.value  # type: ignore
            cur = cur.next[0]

    def iter_desc(self) -> ta.Iterator[T]:
        cur = self._tail
        while cur is not self._head and cur is not None:
            yield cur.value  # type: ignore
            cur = cur.prev  # type: ignore

    def iter_from(self, base: T) -> ta.Iterator[T]:
        cur = self._find(base)
        while cur is not None and self._compare(base, cur.value) > 0:  # type: ignore
            cur = cur.next[0]

        while cur is not None:
            yield cur.value  # type: ignore
            cur = cur.next[0]

    def iter_from_desc(self, base: T) -> ta.Iterator[T]:
        cur = self._find(base)
        while cur is not self._head and self._compare(base, cur.value) < 0:  # type: ignore
            cur = cur.prev  # type: ignore

        while cur is not self._head:
            yield cur.value  # type: ignore
            cur = cur.prev  # type: ignore


##


class SkipListDict(SortedListDict[K, V]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(SkipList(comparator=SortedListDict._item_comparator), *args, **kwargs)  # noqa
