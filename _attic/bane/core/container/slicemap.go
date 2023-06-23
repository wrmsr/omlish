package container

import (
	its "github.com/wrmsr/bane/core/iterators"
	"github.com/wrmsr/bane/core/slices"
	bt "github.com/wrmsr/bane/core/types"
)

//

type SliceMap[K comparable, V any] struct {
	s []bt.Kv[K, V]
	m map[K]int
}

func NewSliceMap[K comparable, V any](it bt.Iterable[bt.Kv[K, V]]) SliceMap[K, V] {
	m := SliceMap[K, V]{}
	if it != nil {
		for it := it.Iterate(); it.HasNext(); {
			c := it.Next()
			m.put(c.K, c.V)
		}
	}
	return m
}

var _ OrderedMap[int, any] = SliceMap[int, any]{}

func (m SliceMap[K, V]) isOrdered() {}

func (m SliceMap[K, V]) Len() int {
	if m.m == nil {
		return 0
	}
	return len(m.s)
}

func (m SliceMap[K, V]) Contains(k K) bool {
	if m.m == nil {
		return false
	}
	_, ok := m.m[k]
	return ok
}

func (m SliceMap[K, V]) Get(k K) V {
	if m.m == nil {
		var z V
		return z
	}
	i, ok := m.m[k]
	if !ok {
		return bt.Zero[V]()
	}
	return m.s[i].V
}

func (m SliceMap[K, V]) TryGet(k K) (V, bool) {
	if m.m == nil {
		var z V
		return z, false
	}
	i, ok := m.m[k]
	if !ok {
		return bt.Zero[V](), false
	}
	return m.s[i].V, true
}

func (m SliceMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	if m.m == nil {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return its.OfSlice(m.s).Iterate()
}

func (m SliceMap[K, V]) ForEach(fn func(bt.Kv[K, V]) bool) bool {
	if m.m == nil {
		return true
	}
	for _, kv := range m.s {
		if !fn(kv) {
			return false
		}
	}
	return true
}

func (m SliceMap[K, V]) IterateFrom(k K) bt.Iterator[bt.Kv[K, V]] {
	if m.m == nil {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	i, ok := m.m[k]
	if !ok {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return its.OfSliceRange(m.s, bt.RangeOf(i, len(m.s), 1)).Iterate()
}

func (m SliceMap[K, V]) ReverseIterate() bt.Iterator[bt.Kv[K, V]] {
	if m.m == nil {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return its.OfSliceRange(m.s, bt.RangeOf(len(m.s)-1, -1, -1)).Iterate()
}

func (m SliceMap[K, V]) ReverseIterateFrom(k K) bt.Iterator[bt.Kv[K, V]] {
	if m.m == nil {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	i, ok := m.m[k]
	if !ok {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return its.OfSliceRange(m.s, bt.RangeOf(i, -1, -1)).Iterate()
}

var _ its.AnyIterable = SliceMap[int, string]{}

func (m SliceMap[K, V]) AnyIterate() bt.Iterator[any] {
	if m.m == nil {
		return its.Empty[any]().Iterate()
	}
	return its.AsAny[bt.Kv[K, V]](m).Iterate()
}

func (m *SliceMap[K, V]) lazyInit() {
	if m.m == nil {
		m.m = make(map[K]int)
	}
}

func (m *SliceMap[K, V]) put(k K, v V) {
	m.lazyInit()
	i, ok := m.m[k]
	if ok {
		m.s[i].V = v
		return
	}
	m.m[k] = len(m.s)
	m.s = append(m.s, bt.KvOf(k, v))
}

func (m *SliceMap[K, V]) delete(k K) {
	m.lazyInit()
	i, ok := m.m[k]
	if !ok {
		return
	}
	m.s = slices.DeleteAt(m.s, i)
	delete(m.m, k)
}

func (m *SliceMap[K, V]) default_(k K, v V) bool {
	m.lazyInit()
	_, ok := m.m[k]
	if ok {
		return false
	}
	m.m[k] = len(m.s)
	m.s = append(m.s, bt.KvOf(k, v))
	return true
}

func (m *SliceMap[K, V]) filter(fn func(kv bt.Kv[K, V]) bool) {
	m.lazyInit()
	for i := 0; i < len(m.s); {
		kv := m.s[i]
		if !fn(kv) {
			m.s = slices.DeleteAt(m.s, i)
			delete(m.m, kv.K)
		} else {
			i++
		}
	}
}

//

type MutSliceMap[K comparable, V any] struct {
	m SliceMap[K, V]
}

func NewMutSliceMap[K comparable, V any](it bt.Iterable[bt.Kv[K, V]]) *MutSliceMap[K, V] {
	return &MutSliceMap[K, V]{m: NewSliceMap[K, V](it)}
}

func (m *MutSliceMap[K, V]) All() []bt.Kv[K, V] {
	return m.m.s
}

var _ MutOrderedMap[int, any] = &MutSliceMap[int, any]{}

func (m *MutSliceMap[K, V]) isMut()     {}
func (m *MutSliceMap[K, V]) isOrdered() {}

func (m *MutSliceMap[K, V]) Len() int                                 { return m.m.Len() }
func (m *MutSliceMap[K, V]) Contains(k K) bool                        { return m.m.Contains(k) }
func (m *MutSliceMap[K, V]) Get(k K) V                                { return m.m.Get(k) }
func (m *MutSliceMap[K, V]) TryGet(k K) (V, bool)                     { return m.m.TryGet(k) }
func (m *MutSliceMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]]        { return m.m.Iterate() }
func (m *MutSliceMap[K, V]) ForEach(fn func(v bt.Kv[K, V]) bool) bool { return m.m.ForEach(fn) }

func (m *MutSliceMap[K, V]) IterateFrom(k K) bt.Iterator[bt.Kv[K, V]] { return m.m.IterateFrom(k) }
func (m *MutSliceMap[K, V]) ReverseIterate() bt.Iterator[bt.Kv[K, V]] { return m.m.ReverseIterate() }
func (m *MutSliceMap[K, V]) ReverseIterateFrom(k K) bt.Iterator[bt.Kv[K, V]] {
	return m.m.ReverseIterateFrom(k)
}

func (m *MutSliceMap[K, V]) Put(k K, v V) {
	m.m.put(k, v)
}

func (m *MutSliceMap[K, V]) Delete(k K) {
	m.m.delete(k)
}

func (m *MutSliceMap[K, V]) Default(k K, v V) bool {
	return m.m.default_(k, v)
}

var _ Decay[Map[int, string]] = &MutSliceMap[int, string]{}

func (m *MutSliceMap[K, V]) Decay() Map[K, V] { return m.m }
