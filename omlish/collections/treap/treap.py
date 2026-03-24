# ruff: noqa: SLF001
# MIT License
#
# Copyright (c) 2022 Gabriel Ochsenhofer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import random
import typing as ta


T = ta.TypeVar('T')

Comparer: ta.TypeAlias = ta.Callable[[T, T], int]


##


@ta.final
class TreapNode(ta.Generic[T]):
    __slots__ = ('_value', '_priority', '_left', '_right', '_count')

    def __init__(
            self,
            *,
            _value: T,
            _priority: int,
            _left: ta.Optional['TreapNode[T]'],
            _right: ta.Optional['TreapNode[T]'],
    ) -> None:
        self._value, self._priority, self._left, self._right = _value, _priority, _left, _right
        self._set_count()

    _count: int

    def _set_count(self) -> None:
        self._count = (
            1 +
            (self._left._count if self._left is not None else 0) +
            (self._right._count if self._right is not None else 0)
        )

    def __repr__(self) -> str:
        return f'TreapNode(value={self._value!r}, priority={self._priority!r}, count={self._count!r})'

    @property
    def value(self) -> T:
        return self._value

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def left(self) -> ta.Optional['TreapNode[T]']:
        return self._left

    @property
    def right(self) -> ta.Optional['TreapNode[T]']:
        return self._right

    @property
    def count(self) -> int:
        return self._count

    def __iter__(self) -> ta.Iterator[T]:
        if self._left is not None:
            yield from self._left
        yield self._value
        if self._right is not None:
            yield from self._right


def _new_priority() -> int:
    return random.getrandbits(32)


def new(value: T, *, priority: int | None = None) -> TreapNode[T]:
    return TreapNode(_value=value, _priority=priority if priority is not None else _new_priority(), _left=None, _right=None)  # noqa


def find(n: TreapNode[T] | None, v: T, c: Comparer[T]) -> TreapNode[T] | None:
    while True:
        if n is None:
            return None
        diff = c(n._value, v)  # noqa
        if diff == 0:
            return n
        elif diff < 0:
            n = n._right  # noqa
        else:
            n = n._left  # noqa


def place(n: TreapNode[T] | None, v: T, c: Comparer[T], *, desc: bool = False) -> list[TreapNode[T]]:
    ret: list[TreapNode[T]] = []
    while True:
        if n is None:
            break
        diff = c(n._value, v)  # noqa
        if diff == 0:
            ret.append(n)
            break
        elif diff < 0:
            if desc:
                ret.append(n)
            n = n._right  # noqa
        else:
            if not desc:
                ret.append(n)
            n = n._left  # noqa
    return ret


def union(
        n: TreapNode[T] | None,
        other: TreapNode[T] | None,
        c: Comparer[T],
        overwrite: bool,
) -> TreapNode[T] | None:
    if n is None:
        return other
    if other is None:
        return n
    if n._priority < other._priority:
        # If we are unioning Tree A (target) and Tree B (source), and overwrite=True (meaning B's values should replace
        # A's on a collision):
        # - If A._priority < B._priority (meaning A becomes the parent of B), the code naturally extracts B's value as
        #   dupe, and value = dupe._value overwrites the root A's value. This is correct.
        # - If B._priority < A._priority (meaning B becomes the parent of A), you swap them so n is now B.
        # - Because n is now B, its baseline value is B's value.
        # - If you didn't flip overwrite, the code would see overwrite=True, find A's value as the dupe, and overwrite
        #   B's value with A's value - which is exactly backward!
        # - By flipping overwrite = not overwrite (making it False), you prevent A from overwriting B, thus preserving
        #   B's value as the root.
        other, n, overwrite = n, other, not overwrite
    left, dupe, right = split(other, n._value, c)
    value = n._value
    if overwrite and dupe is not None:
        value = dupe._value
    left = union(n._left, left, c, overwrite)
    right = union(n._right, right, c, overwrite)
    return TreapNode(_value=value, _priority=n._priority, _left=left, _right=right)


def split(
        n: TreapNode[T] | None,
        v: T,
        c: Comparer[T],
) -> tuple[
        TreapNode[T] | None,
        TreapNode[T] | None,
        TreapNode[T] | None,
]:
    if n is None:
        return None, None, None

    diff = c(n._value, v)

    if diff < 0:
        # n._value < v -> n belongs in the left split. We must recursively split n's right child.
        left_split, dupe, right_split = split(n._right, v, c)

        # Rebuild n with its original left child, and the new left_split as its right child. _set_count() is called
        # safely here because left_split is fully formed.
        new_left = TreapNode(
            _value=n._value,
            _priority=n._priority,
            _left=n._left,
            _right=left_split,
        )
        return new_left, dupe, right_split

    elif diff > 0:
        # n._value > v -> n belongs in the right split. We must recursively split n's left child.
        left_split, dupe, right_split = split(n._left, v, c)

        # Rebuild n with the new right_split as its left child, and its original right child.
        new_right = TreapNode(
            _value=n._value,
            _priority=n._priority,
            _left=right_split,
            _right=n._right,
        )
        return left_split, dupe, new_right

    else:
        # diff == 0 -> We found the split point exactly. Isolate the duplicate node (no children).
        dupe = TreapNode(_value=n._value, _priority=n._priority, _left=None, _right=None)
        return n._left, dupe, n._right


def intersect(
        n: TreapNode[T] | None,
        other: TreapNode[T] | None,
        c: Comparer[T],
) -> TreapNode[T] | None:
    if n is None or other is None:
        return None

    if n._priority < other._priority:
        n, other = other, n

    left, found, right = split(other, n._value, c)
    left = intersect(n._left, left, c)
    right = intersect(n._right, right, c)

    if found is None:
        # TODO: use a destructive join as both left/right are copies
        return _join(left, right)

    return TreapNode(_value=n._value, _priority=n._priority, _left=left, _right=right)


def delete(n: TreapNode[T] | None, v: T, c: Comparer[T]) -> TreapNode[T] | None:
    left, _, right = split(n, v, c)
    return _join(left, right)


def diff(n: TreapNode[T] | None, other: TreapNode[T] | None, c: Comparer[T]) -> TreapNode[T] | None:
    if n is None or other is None:
        return n

    if n._priority >= other._priority:
        left, dupe, right = split(other, n._value, c)
        left, right = diff(n._left, left, c), diff(n._right, right, c)
        if dupe is not None:
            return _join(left, right)
        return TreapNode(_value=n._value, _priority=n._priority, _left=left, _right=right)

    left, _, right = split(n, other._value, c)
    left = diff(left, other._left, c)
    right = diff(right, other._right, c)
    return _join(left, right)


def _join(n: TreapNode[T] | None, other: TreapNode[T] | None) -> TreapNode[T] | None:
    if n is None:
        return other
    if other is None:
        return n

    if n._priority >= other._priority:
        # 'n' is the root. Since all keys in 'n' < all keys in 'other', 'other' must be merged into 'n's right side.
        right_joined = _join(n._right, other)

        return TreapNode(
            _value=n._value,
            _priority=n._priority,
            _left=n._left,
            _right=right_joined,
        )

    else:
        # 'other' is the root. Since all keys in 'n' < all keys in 'other', 'n' must be merged into 'other's left side.
        left_joined = _join(n, other._left)

        return TreapNode(
            _value=other._value,
            _priority=other._priority,
            _left=left_joined,
            _right=other._right,
        )
