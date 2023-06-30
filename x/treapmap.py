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

from . import treap


K = ta.TypeVar('K')
V = ta.TypeVar('V')

Comparer = ta.Callable[[ta.Tuple[K, V], ta.Tuple[K, V]], int]


def key_cmp(fn: ta.Callable[[K, K], int]) -> Comparer[K, V]:
    return lambda t0, t1: fn(t0[0], t1[0])


class TreapMap(ta.Generic[K, V]):
    
    def __init__(
            self,
            *,
            _n: treap.TreapNode[ta.Tuple[K, V]],
            _c: treap.Comparer[ta.Tuple[K, V]],
    ) -> None:
        super().__init__()

        self._c = _c
        self._n = _n

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


"""
type treapMapIterator[K, V any] struct {
    st []*treap.TreapNode[bt.Kv[K, V]]
    n  *treap.TreapNode[bt.Kv[K, V]]
    b  bool
}

var _ bt.Iterator[bt.Kv[int, string]] = &treapMapIterator[int, string]{}

func (i *treapMapIterator[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
    return i
}

func (i *treapMapIterator[K, V]) HasNext() bool {
    return i.n != nil
}

func (i *treapMapIterator[K, V]) Next() bt.Kv[K, V] {
    n := i.n
    if n.Right != nil {
        i.n = n.Right
        for i.n.Left != nil {
            i.st = append(i.st, i.n)
            i.n = i.n.Left
        }
    } else if len(i.st) > 0 {
        i.n = i.st[len(i.st)-1]
        i.st = i.st[:len(i.st)-1]
    } else {
        i.n = nil
    }
    return n.Value
}

func (m TreapMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
    i := &treapMapIterator[K, V]{
        st: make([]*treap.TreapNode[bt.Kv[K, V]], 0, 8),
        n:  m.n,
    }
    for i.n.Left != nil {
        i.st = append(i.st, i.n)
        i.n = i.n.Left
    }
    return i
}

func (m TreapMap[K, V]) ForEach(fn func(kv bt.Kv[K, V]) bool) bool {
    return m.n.ForEach(func(kv bt.Kv[K, V]) bool {
        return fn(kv)
    })
}

func (m TreapMap[K, V]) With(k K, v V) PersistentMap[K, V] {
    node := &treap.TreapNode[bt.Kv[K, V]]{
        bt.KvOf(k, v),
        int(rndu.FastUint32()),
        nil,
        nil,
    }
    n := m.n.Union(node, m.c, true)
    return TreapMap[K, V]{n, m.c}
}

func (m TreapMap[K, V]) Without(k K) PersistentMap[K, V] {
    n := m.n.Delete(bt.KvOf[K, V](k, bt.Zero[V]()), m.c)
    return TreapMap[K, V]{n, m.c}
}

func (m TreapMap[K, V]) Default(k K, v V) PersistentMap[K, V] {
    if _, ok := m.TryGet(k); ok {
        return m
    }
    return m.With(k, v)
}
"""
