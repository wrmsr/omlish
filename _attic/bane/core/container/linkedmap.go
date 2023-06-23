package container

import (
	"fmt"

	its "github.com/wrmsr/bane/core/iterators"
	"github.com/wrmsr/bane/core/sync/pools"
	bt "github.com/wrmsr/bane/core/types"
)

//

type linkedMapNode struct {
	k, v any

	next, prev *linkedMapNode
}

func (n *linkedMapNode) String() string {
	return fmt.Sprintf("%16p{%16p %16p} %v", n, n.next, n.prev, n.k)
}

var linkedMapNodePool = pools.NewDrainPool[*linkedMapNode](func() *linkedMapNode {
	return &linkedMapNode{}
})

//

type LinkedMap[K comparable, V any] struct {
	m map[K]*linkedMapNode

	head, tail *linkedMapNode
}

func NewLinkedMap[K comparable, V any](it bt.Iterable[bt.Kv[K, V]]) LinkedMap[K, V] {
	m := LinkedMap[K, V]{}
	if it != nil {
		for it := it.Iterate(); it.HasNext(); {
			c := it.Next()
			m.put(c.K, c.V)
		}
	}
	return m
}

var _ OrderedMap[int, any] = LinkedMap[int, any]{}

func (m LinkedMap[K, V]) isOrdered() {}

func (m LinkedMap[K, V]) Len() int {
	if m.m == nil {
		return 0
	}
	return len(m.m)
}

func (m LinkedMap[K, V]) Contains(k K) bool {
	if m.m == nil {
		return false
	}
	_, ok := m.m[k]
	return ok
}

func (m LinkedMap[K, V]) Get(k K) V {
	if m.m == nil {
		var z V
		return z
	}
	n, ok := m.m[k]
	if !ok {
		return bt.Zero[V]()
	}
	return n.v.(V)
}

func (m LinkedMap[K, V]) TryGet(k K) (V, bool) {
	if m.m == nil {
		var z V
		return z, false
	}
	n, ok := m.m[k]
	if !ok {
		return bt.Zero[V](), false
	}
	return n.v.(V), true
}

type linkedMapIterator[K comparable, V any] struct {
	n *linkedMapNode
	r bool
}

var _ bt.Iterator[bt.Kv[int, string]] = &linkedMapIterator[int, string]{}

func (l *linkedMapIterator[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	return l
}

func (l *linkedMapIterator[K, V]) HasNext() bool {
	return l.n != nil
}

func (l *linkedMapIterator[K, V]) Next() bt.Kv[K, V] {
	kv := bt.KvOf(l.n.k.(K), l.n.v.(V))
	if l.r {
		l.n = l.n.prev
	} else {
		l.n = l.n.next
	}
	return kv
}

func (m LinkedMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	if m.m == nil {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return &linkedMapIterator[K, V]{n: m.head}
}

func (m LinkedMap[K, V]) ForEach(fn func(bt.Kv[K, V]) bool) bool {
	if m.m == nil {
		return true
	}
	for n := m.head; n != nil; n = n.next {
		if !fn(bt.KvOf(n.k.(K), n.v.(V))) {
			return false
		}
	}
	return true
}

func (m LinkedMap[K, V]) IterateFrom(k K) bt.Iterator[bt.Kv[K, V]] {
	if m.m == nil {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	n, ok := m.m[k]
	if !ok {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return &linkedMapIterator[K, V]{n: n}
}

func (m LinkedMap[K, V]) ReverseIterate() bt.Iterator[bt.Kv[K, V]] {
	if m.m == nil {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return &linkedMapIterator[K, V]{n: m.tail, r: true}
}

func (m LinkedMap[K, V]) ReverseIterateFrom(k K) bt.Iterator[bt.Kv[K, V]] {
	if m.m == nil {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	n, ok := m.m[k]
	if !ok {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return &linkedMapIterator[K, V]{n: n, r: true}
}

var _ its.AnyIterable = LinkedMap[int, string]{}

func (m LinkedMap[K, V]) AnyIterate() bt.Iterator[any] {
	if m.m == nil {
		return its.Empty[any]().Iterate()
	}
	return its.AsAny[bt.Kv[K, V]](m).Iterate()
}

func (m *LinkedMap[K, V]) lazyInit() {
	if m.m == nil {
		m.m = make(map[K]*linkedMapNode)
	}
}

func (m *LinkedMap[K, V]) put(k K, v V) {
	m.delete(k)
	m.lazyInit()

	n := linkedMapNodePool.Get()
	n.k = k
	n.v = v

	n.prev = m.tail
	if m.head == nil {
		m.head = n
	}
	if m.tail != nil {
		m.tail.next = n
	}
	m.tail = n

	m.m[k] = n
}

func (m *LinkedMap[K, V]) delete(k K) {
	if m.m == nil {
		return
	}

	n := m.m[k]
	if n == nil {
		return
	}

	if n.next != nil {
		n.next.prev = n.prev
	}
	if n.prev != nil {
		n.prev.next = n.next
	}

	if m.head == n {
		m.head = n.next
	}
	if m.tail == n {
		m.tail = n.prev
	}

	delete(m.m, k)

	*n = linkedMapNode{}
	linkedMapNodePool.Put(n)
}

func (m *LinkedMap[K, V]) default_(k K, v V) bool {
	m.lazyInit()
	_, ok := m.m[k]
	if ok {
		return false
	}
	m.put(k, v)
	return true
}

//

type MutLinkedMap[K comparable, V any] struct {
	m LinkedMap[K, V]
}

func NewMutLinkedMap[K comparable, V any](it bt.Iterable[bt.Kv[K, V]]) *MutLinkedMap[K, V] {
	return &MutLinkedMap[K, V]{m: NewLinkedMap[K, V](it)}
}

var _ MutOrderedMap[int, any] = &MutLinkedMap[int, any]{}

func (m *MutLinkedMap[K, V]) isMut()     {}
func (m *MutLinkedMap[K, V]) isOrdered() {}

func (m *MutLinkedMap[K, V]) Len() int                                 { return m.m.Len() }
func (m *MutLinkedMap[K, V]) Contains(k K) bool                        { return m.m.Contains(k) }
func (m *MutLinkedMap[K, V]) Get(k K) V                                { return m.m.Get(k) }
func (m *MutLinkedMap[K, V]) TryGet(k K) (V, bool)                     { return m.m.TryGet(k) }
func (m *MutLinkedMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]]        { return m.m.Iterate() }
func (m *MutLinkedMap[K, V]) ForEach(fn func(v bt.Kv[K, V]) bool) bool { return m.m.ForEach(fn) }

func (m *MutLinkedMap[K, V]) IterateFrom(k K) bt.Iterator[bt.Kv[K, V]] { return m.m.IterateFrom(k) }
func (m *MutLinkedMap[K, V]) ReverseIterate() bt.Iterator[bt.Kv[K, V]] { return m.m.ReverseIterate() }
func (m *MutLinkedMap[K, V]) ReverseIterateFrom(k K) bt.Iterator[bt.Kv[K, V]] {
	return m.m.ReverseIterateFrom(k)
}

func (m *MutLinkedMap[K, V]) Put(k K, v V) {
	m.m.put(k, v)
}

func (m *MutLinkedMap[K, V]) Delete(k K) {
	m.m.delete(k)
}

func (m *MutLinkedMap[K, V]) Default(k K, v V) bool {
	return m.m.default_(k, v)
}

var _ Decay[Map[int, string]] = &MutLinkedMap[int, string]{}

func (m *MutLinkedMap[K, V]) Decay() Map[K, V] { return m.m }
