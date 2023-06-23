package container

import (
	"golang.org/x/exp/constraints"

	"github.com/wrmsr/bane/core/container/rbtree"
	bt "github.com/wrmsr/bane/core/types"
)

//

type RbTreeMap[K, V any] struct {
	t rbtree.RbTree

	less bt.LessImpl[K]
}

func kvLessImpl[K, V any](less bt.LessImpl[K]) bt.LessImpl[any] {
	return func(l, r any) bool {
		return less(bt.AsKey[K, V](l), bt.AsKey[K, V](r))
	}
}

func NewRbTreeMap[K, V any](less bt.LessImpl[K], it bt.Iterable[bt.Kv[K, V]]) RbTreeMap[K, V] {
	if less == nil {
		panic("must provide less impl")
	}
	m := RbTreeMap[K, V]{
		t: rbtree.RbTree{
			Less: kvLessImpl[K, V](less),
		},
		less: less,
	}
	if it != nil {
		for it := it.Iterate(); it.HasNext(); {
			kv := it.Next()
			m.put(kv.K, kv.V)
		}
	}
	return m
}

var _ Map[int, string] = RbTreeMap[int, string]{}

func (m RbTreeMap[K, V]) Len() int {
	return m.t.Len()
}

func (m RbTreeMap[K, V]) Contains(k K) bool {
	_, ok := m.TryGet(k)
	return ok
}

func (m RbTreeMap[K, V]) Get(k K) V {
	v, _ := m.TryGet(k)
	return v
}

func (m RbTreeMap[K, V]) TryGet(k K) (V, bool) {
	if n := m.t.Find(k); n != nil {
		return n.Item.(bt.Kv[K, V]).V, true
	}
	var z V
	return z, false
}

type rbTreeMapIterator[K, V any] struct {
	i rbtree.RbIter
}

var _ bt.Iterator[bt.Kv[int, string]] = &rbTreeMapIterator[int, string]{}

func (i *rbTreeMapIterator[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	return i
}

func (i *rbTreeMapIterator[K, V]) HasNext() bool {
	return i.i.Ok()
}

func (i *rbTreeMapIterator[K, V]) Next() bt.Kv[K, V] {
	kv := i.i.Item().(bt.Kv[K, V])
	i.i.Right()
	return kv
}

func (m RbTreeMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	return &rbTreeMapIterator[K, V]{i: rbtree.RbIterAt(m.t.Min())}
}

func (m RbTreeMap[K, V]) ForEach(fn func(v bt.Kv[K, V]) bool) bool {
	for it := rbtree.RbIterAt(m.t.Min()); it.Ok(); it.Right() {
		if !fn(it.Item().(bt.Kv[K, V])) {
			return false

		}
	}
	return true
}

func (m *RbTreeMap[K, V]) put(k K, v V) {
	m.t.Insert(bt.KvOf(k, v))
}

func (m *RbTreeMap[K, V]) delete(k K) {
	if found := m.t.Find(k); found != nil {
		m.t.Delete(found)
	}
}

func (m *RbTreeMap[K, V]) default_(k K, v V) bool {
	if m.Contains(k) {
		return false
	}
	m.put(k, v)
	return true
}

func (m *RbTreeMap[K, V]) clear() {
	m.t.Clear()
}

//

type MutRbTreeMap[K, V any] struct {
	m RbTreeMap[K, V]
}

func NewMutRbTreeMap[K, V any](less bt.LessImpl[K], it bt.Iterable[bt.Kv[K, V]]) *MutRbTreeMap[K, V] {
	return &MutRbTreeMap[K, V]{m: NewRbTreeMap[K, V](less, it)}
}

var _ MutMap[int, string] = &MutRbTreeMap[int, string]{}

func (m *MutRbTreeMap[K, V]) isMut() {}

func (m *MutRbTreeMap[K, V]) Len() int                                 { return m.m.Len() }
func (m *MutRbTreeMap[K, V]) Contains(k K) bool                        { return m.m.Contains(k) }
func (m *MutRbTreeMap[K, V]) Get(k K) V                                { return m.m.Get(k) }
func (m *MutRbTreeMap[K, V]) TryGet(k K) (V, bool)                     { return m.m.TryGet(k) }
func (m *MutRbTreeMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]]        { return m.m.Iterate() }
func (m *MutRbTreeMap[K, V]) ForEach(fn func(v bt.Kv[K, V]) bool) bool { return m.m.ForEach(fn) }

func (m *MutRbTreeMap[K, V]) Put(k K, v V) {
	m.m.put(k, v)
}

func (m *MutRbTreeMap[K, V]) Delete(k K) {
	m.m.delete(k)
}

func (m *MutRbTreeMap[K, V]) Default(k K, v V) bool {
	return m.m.default_(k, v)
}

var _ Decay[Map[int, string]] = &MutRbTreeMap[int, string]{}

func (m *MutRbTreeMap[K, V]) Decay() Map[K, V] { return m.m }

//

type PrimitiveRbTreeMap[K constraints.Ordered, V any] struct {
	m RbTreeMap[K, V]
}

func NewPrimitiveRbTreeMap[K constraints.Ordered, V any](it bt.Iterable[bt.Kv[K, V]]) PrimitiveRbTreeMap[K, V] {
	return PrimitiveRbTreeMap[K, V]{m: NewRbTreeMap[K, V](bt.CmpLessImpl(bt.OrderedCmp[K]), it)}
}

var _ Map[int, string] = PrimitiveRbTreeMap[int, string]{}

func (m PrimitiveRbTreeMap[K, V]) Len() int                          { return m.m.Len() }
func (m PrimitiveRbTreeMap[K, V]) Contains(k K) bool                 { return m.m.Contains(k) }
func (m PrimitiveRbTreeMap[K, V]) Get(k K) V                         { return m.m.Get(k) }
func (m PrimitiveRbTreeMap[K, V]) TryGet(k K) (V, bool)              { return m.m.TryGet(k) }
func (m PrimitiveRbTreeMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] { return m.m.Iterate() }

func (m PrimitiveRbTreeMap[K, V]) ForEach(fn func(v bt.Kv[K, V]) bool) bool {
	return m.m.ForEach(fn)
}

//

type PrimitiveMutRbTreeMap[K constraints.Ordered, V any] struct {
	m RbTreeMap[K, V]
}

func NewPrimitiveMutRbTreeMap[K constraints.Ordered, V any](it bt.Iterable[bt.Kv[K, V]]) *PrimitiveMutRbTreeMap[K, V] {
	return &PrimitiveMutRbTreeMap[K, V]{m: NewRbTreeMap[K, V](bt.CmpLessImpl(bt.OrderedCmp[K]), it)}
}

var _ MutMap[int, string] = &PrimitiveMutRbTreeMap[int, string]{}

func (m *PrimitiveMutRbTreeMap[K, V]) isMut() {}

func (m *PrimitiveMutRbTreeMap[K, V]) Len() int                          { return m.m.Len() }
func (m *PrimitiveMutRbTreeMap[K, V]) Contains(k K) bool                 { return m.m.Contains(k) }
func (m *PrimitiveMutRbTreeMap[K, V]) Get(k K) V                         { return m.m.Get(k) }
func (m *PrimitiveMutRbTreeMap[K, V]) TryGet(k K) (V, bool)              { return m.m.TryGet(k) }
func (m *PrimitiveMutRbTreeMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] { return m.m.Iterate() }

func (m *PrimitiveMutRbTreeMap[K, V]) ForEach(fn func(v bt.Kv[K, V]) bool) bool {
	return m.m.ForEach(fn)
}

func (m *PrimitiveMutRbTreeMap[K, V]) Put(k K, v V)          { m.m.put(k, v) }
func (m *PrimitiveMutRbTreeMap[K, V]) Delete(k K)            { m.m.delete(k) }
func (m *PrimitiveMutRbTreeMap[K, V]) Default(k K, v V) bool { return m.m.default_(k, v) }

var _ Decay[Map[int, string]] = &MutRbTreeMap[int, string]{}

func (m *PrimitiveMutRbTreeMap[K, V]) Decay() Map[K, V] { return m.m }
