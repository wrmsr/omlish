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
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')
Comparer = ta.Callable[[T, T], int]


@dc.dataclass(frozen=True)
class TreapNode(ta.Generic[T]):
    value: T
    priority: int
    left: ta.Optional['TreapNode[T]']
    right: ta.Optional['TreapNode[T]']

    def __iter__(self) -> ta.Iterator[T]:
        if self.left is not None:
            yield from self.left
        yield self.value
        if self.right is not None:
            yield from self.right


def find(n: TreapNode[T], v: T, c: Comparer[T]) -> ta.Optional[TreapNode[T]]:
    while True:
        if n is None:
            return None
        diff = c(n.value, v)
        if diff == 0:
            return n
        elif diff < 0:
            n = n.right
        else:
            n = n.left


def union(
        n: ta.Optional[TreapNode[T]],
        other: ta.Optional[TreapNode[T]],
        c: Comparer[T],
        overwrite: bool,
) -> TreapNode[T]:
    if n is None:
        return other
    if other is None:
        return n
    if n.priority < other.priority:
        other, n, overwrite = n, other, not overwrite
    left, dupe, right = split(n.value, c)
    value = n.value
    if overwrite and dupe is not None:
        value = dupe.value
    left = union(n.left, left, c, overwrite)
    right = union(n.right, right, c, overwrite)
    return TreapNode(value, n.priority, left, right)


def split(
        n: TreapNode[T],
        v: T,
        c: Comparer[T],
) -> ta.Tuple[
    ta.Optional[TreapNode[T]],
    ta.Optional[TreapNode[T]],
    ta.Optional[TreapNode[T]],
]:
    tmp = TreapNode(None, 0, None, None)
    leftp, rightp = [tmp, 'l'], [tmp, 'r']

    def setp(p, o):
        t, s = p
        if s == 'l':
            t.left = o
        elif s == 'r':
            t.right = o
        else:
            raise ValueError(p)

    while True:
        if n is None:
            setp(leftp, None)
            setp(rightp, None)
            return tmp.left, None, tmp.right

        d = c(n.value, v)
        if d < 0:
            root = TreapNode(n.value, n.priority, n.left, None)
            setp(leftp, root)
            leftp[0], leftp[1] = root, 'r'
            n = n.right
        elif d > 0:
            root = TreapNode(n.value, n.priority, None, n.right)
            setp(rightp, root)
            rightp[0], rightp[1] = root, 'l'
            n = n.left
        else:
            root = TreapNode(n.value, n.priority, None, None)
            setp(leftp, n.left)
            setp(rightp, n.right)
            return tmp.left, root, tmp.right


def intersect(
        n: ta.Optional[TreapNode[T]],
        other: ta.Optional[TreapNode[T]],
        c: Comparer[T],
) -> ta.Optional[TreapNode[T]]:
    if n is None or other is None:
        return None

    if n.priority < other.priority:
        n, other = other, n

    left, found, right = split(other, n.value, c)
    left = intersect(n.left, left, c)
    right = intersect(n.right, right, c)

    if found is None:
        # TODO: use a destructive join as both left/right are copies
        return _join(left, right)

    return TreapNode(n.value, n.priority, left, right)


def delete(n: TreapNode[T], v: T, c: Comparer[T]) -> TreapNode[T]:
    left, _, right = split(n, v, c)
    return _join(left, right)


def diff(n: TreapNode[T], other: TreapNode[T], c: Comparer[T]) -> ta.Optional[TreapNode[T]]:
    if n is None or other is None:
        return n

    # TODO -- use count
    if n.priority >= other.priority:
        left, dupe, right = split(other, n.value, c)
        left, right = diff(n.left, left, c), diff(n.right, right, c)
        if dupe is not None:
            return _join(left, right)
        return TreapNode(n.value, n.priority, left, right)

    left, _, right = split(n, other.value, c)
    left = diff(left, other.left, c)
    right = diff(right, other.right, c)
    return _join(left, right)


def _join(n: TreapNode[T], other: TreapNode[T]) -> ta.Optional[TreapNode[T]]:
    result: ta.Optional[TreapNode[T]] = None
    resultp = [None, None]

    def setresultp(o):
        t, s = resultp
        if t is None:
            nonlocal result
            result = o
        elif s == 'l':
            t.left = o
        elif s == 'r':
            t.right = o
        else:
            raise ValueError(resultp)

    while True:
        if n is None:
            setresultp(other)
            return result

        if other is None:
            setresultp(n)
            return result

        if n.priority <= other.priority:
            root = TreapNode(n.value, n.priority, n.left, None)
            setresultp(root)
            resultp[0], resultp[1] = root, 'r'
            n = n.right
        else:
            root = TreapNode(other.value, other.priority, None, other.right)
            setresultp(root)
            resultp[0], resultp[1] = root, 'l'
            other = other.left
