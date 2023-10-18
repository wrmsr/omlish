"""
MIT License

Copyright (c) 2022 Gabriel Ochsenhofer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import typing as ta


T = ta.TypeVar('T')
Comparer = ta.Callable[[T, T], int]


class TreapNode(ta.Generic[T]):
    __slots__ = ('_value', '_priority', '_left', '_right')

    def __init__(
            self,
            *,
            _value: T,
            _priority: int,
            _left: ta.Optional['TreapNode[T]'],
            _right: ta.Optional['TreapNode[T]'],
    ) -> None:
        super().__init__()

        self._value = _value
        self._priority = _priority
        self._left = _left
        self._right = _right

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

    def __iter__(self) -> ta.Iterator[T]:
        if self._left is not None:
            yield from self._left
        yield self._value
        if self._right is not None:
            yield from self._right


def find(n: ta.Optional[TreapNode[T]], v: T, c: Comparer[T]) -> ta.Optional[TreapNode[T]]:
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


def union(
        n: ta.Optional[TreapNode[T]],
        other: ta.Optional[TreapNode[T]],
        c: Comparer[T],
        overwrite: bool,
) -> ta.Optional[TreapNode[T]]:
    if n is None:
        return other
    if other is None:
        return n
    if n._priority < other._priority:
        other, n, overwrite = n, other, not overwrite
    left, dupe, right = split(other, n._value, c)
    value = n._value
    if overwrite and dupe is not None:
        value = dupe._value
    left = union(n._left, left, c, overwrite)
    right = union(n._right, right, c, overwrite)
    return TreapNode(_value=value, _priority=n._priority, _left=left, _right=right)


def split(
        n: ta.Optional[TreapNode[T]],
        v: T,
        c: Comparer[T],
) -> tuple[
    ta.Optional[TreapNode[T]],
    ta.Optional[TreapNode[T]],
    ta.Optional[TreapNode[T]],
]:
    tmp: TreapNode[T] = TreapNode(_value=None, _priority=0, _left=None, _right=None)  # type: ignore
    leftp, rightp = [tmp, 'l'], [tmp, 'r']

    def setp(p, o):
        t, s = p
        if s == 'l':
            t._left = o
        elif s == 'r':
            t._right = o
        else:
            raise ValueError(p)

    cur: ta.Optional[TreapNode[T]] = n
    while True:
        if cur is None:
            setp(leftp, None)
            setp(rightp, None)
            return tmp._left, None, tmp._right  # noqa

        d = c(cur._value, v)
        if d < 0:
            root = TreapNode(_value=cur._value, _priority=cur._priority, _left=cur._left, _right=None)
            setp(leftp, root)
            leftp[0], leftp[1] = root, 'r'
            cur = cur._right
        elif d > 0:
            root = TreapNode(_value=cur._value, _priority=cur._priority, _left=None, _right=cur._right)
            setp(rightp, root)
            rightp[0], rightp[1] = root, 'l'
            cur = cur._left
        else:
            root = TreapNode(_value=cur._value, _priority=cur._priority, _left=None, _right=None)
            setp(leftp, cur._left)
            setp(rightp, cur._right)
            return tmp._left, root, tmp._right


def intersect(
        n: ta.Optional[TreapNode[T]],
        other: ta.Optional[TreapNode[T]],
        c: Comparer[T],
) -> ta.Optional[TreapNode[T]]:
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


def delete(n: ta.Optional[TreapNode[T]], v: T, c: Comparer[T]) -> ta.Optional[TreapNode[T]]:
    left, _, right = split(n, v, c)
    return _join(left, right)


def diff(n: ta.Optional[TreapNode[T]], other: ta.Optional[TreapNode[T]], c: Comparer[T]) -> ta.Optional[TreapNode[T]]:
    if n is None or other is None:
        return n

    # TODO -- use count
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


def _join(n: ta.Optional[TreapNode[T]], other: ta.Optional[TreapNode[T]]) -> ta.Optional[TreapNode[T]]:
    result: ta.Optional[TreapNode[T]] = None
    resultp: list[ta.Any] = [None, None]

    def setresultp(o):
        t, s = resultp
        if t is None:
            nonlocal result
            result = o
        elif s == 'l':
            t._left = o
        elif s == 'r':
            t._right = o
        else:
            raise ValueError(resultp)

    cur: ta.Optional[TreapNode[T]] = n
    while True:
        if cur is None:
            setresultp(other)
            return result

        if other is None:
            setresultp(cur)
            return result

        if cur._priority <= other._priority:
            root = TreapNode(_value=cur._value, _priority=cur._priority, _left=cur._left, _right=None)
            setresultp(root)
            resultp[0], resultp[1] = root, 'r'
            cur = cur._right
        else:
            root = TreapNode(_value=other._value, _priority=other._priority, _left=None, _right=other._right)
            setresultp(root)
            resultp[0], resultp[1] = root, 'l'
            other = other._left
