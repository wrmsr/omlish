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
import random
import typing as ta

from . import treap


K = ta.TypeVar('K')
V = ta.TypeVar('V')

Comparer = ta.Callable[[ta.Tuple[K, V], ta.Tuple[K, V]], int]


def key_cmp(fn: ta.Callable[[K, K], int]) -> Comparer[K, V]:
    return lambda t0, t1: fn(t0[0], t1[0])


class TreapMap(ta.Generic[K, V]):
    __slots__ = ('_n', '_c')

    def __init__(
            self,
            *,
            _n: ta.Optional[treap.TreapNode[ta.Tuple[K, V]]],
            _c: treap.Comparer[ta.Tuple[K, V]],
    ) -> None:
        super().__init__()

        self._n = _n
        self._c = _c

    def __len__(self) -> int:
        # TODO: memo
        # TODO: itertools lol
        result = 0
        for _ in self._n:
            result += 1
        return result

    def __contains__(self, item: K) -> bool:
        try:
            self[item]  # noqa
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, item: K) -> V:
        n = treap.find(self._n, (item, None), self._c)
        if n is None:
            raise KeyError(item)
        return n.value

    def iterate(self) -> 'TreapMapIterator[K, V]':
        i = TreapMapIterator(
            _st=[],
            _n=self._n,
            _b=False,
        )
        while i._n.left is not None:  # noqa
            i._st.append(i._n)  # noqa
            i._n = i._n.left  # noqa
        return i

    def with_(self, k: K, v: V) -> 'TreapMap[K, V]':
        node = treap.TreapNode(
            _value=(k, v),
            _priority=int(random.random() * 0xFFFFFFFF),
            _left=None,
            _right=None,
        )
        n = treap.union(self._n, node, self._c, True)
        return TreapMap(_n=n, _c=self._c)

    def without_(self, k: K) -> 'TreapMap[K, V]':
        n = treap.delete(self._n, (k, None), self._c)
        return TreapMap(_n=n, _c=self._c)

    def default(self, k: K, v: V) -> 'TreapMap[K, V]':
        try:
            self[k]  # noqa
        except KeyError:
            return self.with_(k, v)
        else:
            return self


class TreapMapIterator(ta.Generic[K, V]):
    __slots__ = ('_st', '_n', '_b')

    def __init__(
            self,
            *,
            _st: ta.List[treap.TreapNode[ta.Tuple[K, V]]],
            _n: ta.Optional[treap.TreapNode[ta.Tuple[K, V]]],
            _b: bool,
    ) -> None:
        super().__init__()

        self._st = _st
        self._n = _n
        self._b = _b

    def has_next(self) -> bool:
        return self._n is not None

    def next(self) -> ta.Tuple[K, V]:
        n = self._n
        if n.right is not None:
            self._n = n.right
            while self._n.left is not None:
                self._st.append(self._n)
                self._n = self._n.left
        elif len(self._st) > 0:
            self._n = self._st[-1]
            self._st.pop()
        else:
            self._n = None
        return n.value
