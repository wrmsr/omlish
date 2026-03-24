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
import abc
import typing as ta

from ... import lang
from ..persistent import PersistentMapping
from ..sorted import SortedItems
from ..utils import key_cmp
from . import treap


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


@ta.final
class TreapMap(PersistentMapping[K, V], SortedItems[K, V]):
    __slots__ = ('_n', '_c')

    def __init__(
            self,
            *,
            _n: treap.TreapNode[tuple[K, V]] | None,
            _c: treap.Comparer[tuple[K, V]],
    ) -> None:
        self._n, self._c = _n, _c

    def __len__(self) -> int:
        return self._n.count if self._n is not None else 0

    def __contains__(self, item: K) -> bool:  # type: ignore[override]
        try:
            self[item]  # noqa
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, item: K) -> V:
        n = treap.find(self._n, (item, None), self._c)  # type: ignore
        if n is None:
            raise KeyError(item)
        return n.value[1]

    def __iter__(self) -> ta.Iterator[K]:
        i = self.items()
        while i.has_next():
            yield i.next()[0]

    def items(self) -> 'TreapMapIterator[K, V]':  # type: ignore[override]
        i = TreapMapIterator(_st=[], _n=self._n)
        while (n := i._n) is not None and n.left is not None:  # noqa
            i._st.append(n)  # noqa
            i._n = n.left  # noqa
        return i

    def items_desc(self) -> 'TreapMapReverseIterator[K, V]':
        i = TreapMapReverseIterator(_st=[], _n=self._n)
        while (n := i._n) is not None and n.right is not None:  # noqa
            i._st.append(n)  # noqa
            i._n = n.right  # noqa
        return i

    def items_from(self, k: K) -> 'TreapMapIterator[K, V]':
        lst = treap.place(self._n, (k, None), self._c)  # type: ignore
        i = TreapMapIterator(_st=lst, _n=lst.pop() if lst else None)
        return i

    def items_from_desc(self, k: K) -> 'TreapMapReverseIterator[K, V]':
        lst = treap.place(self._n, (k, None), self._c, desc=True)  # type: ignore
        i = TreapMapReverseIterator(_st=lst, _n=lst.pop() if lst else None)
        return i

    def with_(self, k: K, v: V) -> 'TreapMap[K, V]':
        node = treap.new((k, v))
        n = treap.union(self._n, node, self._c, True)
        return TreapMap(_n=n, _c=self._c)

    def without(self, k: K) -> 'TreapMap[K, V]':
        n = treap.delete(self._n, (k, None), self._c)  # type: ignore
        return TreapMap(_n=n, _c=self._c)

    def default(self, k: K, v: V) -> 'TreapMap[K, V]':
        try:
            self[k]  # noqa
        except KeyError:
            return self.with_(k, v)
        else:
            return self


def new_treap_map(
        items: ta.Iterable[tuple[K, V]] | None = None,
        *,
        cmp: ta.Callable[[K, K], int] | None = None,
) -> TreapMap[K, V]:
    m: TreapMap[K, V] = TreapMap(_n=None, _c=key_cmp(cmp if cmp is not None else lang.cmp))
    if items is not None:
        for k, v in items:
            m = m.with_(k, v)
    return m


##


class BaseTreapMapIterator(lang.Abstract, ta.Iterator[tuple[K, V]], ta.Generic[K, V]):
    __slots__ = ('_st', '_n')

    def __init__(
            self,
            *,
            _st: list[treap.TreapNode[tuple[K, V]]],
            _n: treap.TreapNode[tuple[K, V]] | None,
    ) -> None:
        self._st, self._n = _st, _n

    def __iter__(self) -> ta.Self:
        return self

    def __next__(self) -> tuple[K, V]:
        return self.next()

    def has_next(self) -> bool:
        return self._n is not None

    @abc.abstractmethod
    def next(self) -> tuple[K, V]:
        raise NotImplementedError


@ta.final
class TreapMapIterator(BaseTreapMapIterator[K, V]):
    __slots__ = BaseTreapMapIterator.__slots__  # noqa

    def next(self) -> tuple[K, V]:
        n = self._n
        if n is None:
            raise StopIteration
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


@ta.final
class TreapMapReverseIterator(BaseTreapMapIterator[K, V]):
    __slots__ = BaseTreapMapIterator.__slots__  # noqa

    def next(self) -> tuple[K, V]:
        n = self._n
        if n is None:
            raise StopIteration
        if n.left is not None:
            self._n = n.left
            while self._n.right is not None:
                self._st.append(self._n)
                self._n = self._n.right
        elif len(self._st) > 0:
            self._n = self._st[-1]
            self._st.pop()
        else:
            self._n = None
        return n.value
