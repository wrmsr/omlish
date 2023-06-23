package container

import (
	"fmt"

	its "github.com/wrmsr/bane/core/iterators"
	"github.com/wrmsr/bane/core/sync/pools"
	bt "github.com/wrmsr/bane/core/types"
)

//

type hashEqMapNode struct {
	k, v any

	h uintptr

	next, prev *hashEqMapNode
}

func (n *hashEqMapNode) String() string {
	return fmt.Sprintf("%16p{%16p %16p %16x} %v", n, n.next, n.prev, n.h, n.k)
}

var hashEqMapNodePool = pools.NewDrainPool[*hashEqMapNode](func() *hashEqMapNode {
	return &hashEqMapNode{}
})

//

type HashEqMap[K, V any] struct {
	he bt.HashEqImpl[K]

	head, tail *hashEqMapNode

	m map[uintptr]*hashEqMapNode
	l int
}

func NewHashEqMap[K, V any](he bt.HashEqImpl[K], it bt.Iterable[bt.Kv[K, V]]) HashEqMap[K, V] {
	m := HashEqMap[K, V]{he: he}
	if it != nil {
		for it := it.Iterate(); it.HasNext(); {
			c := it.Next()
			m.put(c.K, c.V)
		}
	}
	return m
}

var _ Map[int, string] = HashEqMap[int, string]{}

func (m HashEqMap[K, V]) Len() int {
	return m.l
}

func (m HashEqMap[K, V]) Contains(k K) bool {
	_, ok := m.TryGet(k)
	return ok
}

func (m HashEqMap[K, V]) Get(k K) V {
	v, _ := m.TryGet(k)
	return v
}

func (m HashEqMap[K, V]) getNode(k K, h uintptr) *hashEqMapNode {
	for cur := m.m[h]; cur != nil && cur.h == h; cur = cur.prev {
		if m.he.Eq(k, cur.k.(K)) {
			return cur
		}
	}
	return nil
}

func (m HashEqMap[K, V]) TryGet(k K) (V, bool) {
	if n := m.getNode(k, m.he.Hash(k)); n != nil {
		return n.v.(V), true
	}
	var z V
	return z, false
}

type hashEqMapIterator[K, V any] struct {
	n *hashEqMapNode
}

var _ bt.Iterator[bt.Kv[int, string]] = &hashEqMapIterator[int, string]{}

func (i *hashEqMapIterator[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	return i
}

func (i *hashEqMapIterator[K, V]) HasNext() bool {
	return i.n.next != nil
}

func (i *hashEqMapIterator[K, V]) Next() bt.Kv[K, V] {
	kv := bt.KvOf(i.n.k.(K), i.n.v.(V))
	i.n = i.n.next
	return kv
}

func (m HashEqMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	return &hashEqMapIterator[K, V]{m.head}
}

func (m HashEqMap[K, V]) ForEach(fn func(v bt.Kv[K, V]) bool) bool {
	for cur := m.head; cur != nil; cur = cur.next {
		if !fn(bt.KvOf(cur.k.(K), cur.v.(V))) {
			return false
		}
	}
	return true
}

func (m *HashEqMap[K, V]) lazyInit() {
	// FIXME: default ops
}

func (m *HashEqMap[K, V]) put(k K, v V) {
	m.lazyInit()

	h := m.he.Hash(k)
	if n := m.getNode(k, h); n != nil {
		n.v = v
		return
	}

	n := hashEqMapNodePool.Get()
	n.k = k
	n.v = v
	n.h = h

	p := m.m[h]

	if p != nil {
		n.next = p
		n.prev = p.prev

		if p.prev != nil {
			p.prev.next = n
		}
		p.prev = n

		if m.tail == nil {
			m.tail = n
		}

	} else {
		n.prev = m.tail

		if m.tail != nil {
			m.tail.next = n
		}
		m.tail = n

		m.m[h] = n
	}

	if m.head == p {
		m.head = n
	}

	m.l++
}

func (m *HashEqMap[K, V]) verify() {
	i := 0
	var prev *hashEqMapNode
	for cur := m.head; cur != nil; prev, cur = cur, cur.next {
		if cur.prev != prev {
			panic(cur)
		}
		i++
	}
	if prev != m.tail {
		panic(prev)
	}
	if i != m.l {
		panic(m.l)
	}
}

func (m *HashEqMap[K, V]) print() {
	for cur := m.head; cur != nil; cur = cur.next {
		fmt.Println(cur)
	}
	fmt.Println()
}

func (m *HashEqMap[K, V]) delete(k K) {
	if m.m == nil {
		return
	}

	h := m.he.Hash(k)
	n := m.getNode(k, h)
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

	if mn := m.m[h]; mn == n {
		if n.prev != nil {
			m.m[h] = n.prev
		} else {
			delete(m.m, h)
		}
	}

	m.l--

	*n = hashEqMapNode{}
	hashEqMapNodePool.Put(n)
}

func (m *HashEqMap[K, V]) default_(k K, v V) bool {
	m.lazyInit()

	if _, ok := m.TryGet(k); ok {
		return false
	}
	m.put(k, v)
	return true
}

func (m *HashEqMap[K, V]) clear() {
	if m.m == nil {
		return
	}

	for cur := m.head; cur != nil; cur = cur.next {
		*cur = hashEqMapNode{}
		hashEqMapNodePool.Put(cur)
	}
	m.head = nil
	m.tail = nil
	m.m = nil
	m.l = 0
}

//

type MutHashEqMap[K, V any] struct {
	m HashEqMap[K, V]
}

func NewMutHashEqMap[K, V any](he bt.HashEqImpl[K], it bt.Iterable[bt.Kv[K, V]]) *MutHashEqMap[K, V] {
	return &MutHashEqMap[K, V]{m: NewHashEqMap[K, V](he, it)}
}

var _ MutMap[int, string] = &MutHashEqMap[int, string]{}

func (m *MutHashEqMap[K, V]) isMut() {}

func (m *MutHashEqMap[K, V]) Len() int                                 { return m.m.Len() }
func (m *MutHashEqMap[K, V]) Contains(k K) bool                        { return m.m.Contains(k) }
func (m *MutHashEqMap[K, V]) Get(k K) V                                { return m.m.Get(k) }
func (m *MutHashEqMap[K, V]) TryGet(k K) (V, bool)                     { return m.m.TryGet(k) }
func (m *MutHashEqMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]]        { return m.m.Iterate() }
func (m *MutHashEqMap[K, V]) ForEach(fn func(v bt.Kv[K, V]) bool) bool { return m.m.ForEach(fn) }

func (m *MutHashEqMap[K, V]) Put(k K, v V) {
	m.m.put(k, v)
}

func (m *MutHashEqMap[K, V]) Delete(k K) {
	m.m.delete(k)
}

func (m *MutHashEqMap[K, V]) Default(k K, v V) bool {
	return m.m.default_(k, v)
}

var _ Decay[Map[int, string]] = &MutHashEqMap[int, string]{}

func (m *MutHashEqMap[K, V]) Decay() Map[K, V] { return m.m }

//

func NewHashEqSet[K any](he bt.HashEqImpl[K], it bt.Iterable[K]) Set[K] {
	var kvs bt.Iterable[bt.Kv[K, struct{}]]
	if it != nil {
		kvs = its.StubKvs(it)
	}
	return NewMapSet[K, struct{}](NewHashEqMap[K, struct{}](he, kvs))
}

func NewMutHashEqSet[K any](he bt.HashEqImpl[K], it bt.Iterable[K]) MutSet[K] {
	var kvs bt.Iterable[bt.Kv[K, struct{}]]
	if it != nil {
		kvs = its.StubKvs(it)
	}
	return NewMutMapSet[K, struct{}](NewMutHashEqMap[K, struct{}](he, kvs))
}
