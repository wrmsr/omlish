package container

import (
	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

//

type StdMap[K comparable, V any] struct {
	m map[K]V
}

func NewStdMap[K comparable, V any](it bt.Iterable[bt.Kv[K, V]]) StdMap[K, V] {
	r := StdMap[K, V]{}
	if it != nil {
		m := make(map[K]V)
		for it := it.Iterate(); it.HasNext(); {
			c := it.Next()
			m[c.K] = c.V
		}
		r.m = m
	}
	return r
}

var _ Map[int, any] = StdMap[int, any]{}

func (m StdMap[K, V]) Len() int {
	if m.m == nil {
		return 0
	}
	return len(m.m)
}

func (m StdMap[K, V]) Contains(k K) bool {
	if m.m == nil {
		return false
	}
	_, ok := m.m[k]
	return ok
}

func (m StdMap[K, V]) Get(k K) V {
	if m.m == nil {
		var z V
		return z
	}
	return m.m[k]
}

func (m StdMap[K, V]) TryGet(k K) (V, bool) {
	if m.m == nil {
		var z V
		return z, false
	}
	v, ok := m.m[k]
	return v, ok
}

func (m StdMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	if m.m == nil {
		its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return its.OfMap[K, V](m.m).Iterate()
}

func (m StdMap[K, V]) ForEach(fn func(bt.Kv[K, V]) bool) bool {
	if m.m == nil {
		return true
	}
	for k, v := range m.m {
		if !fn(bt.KvOf(k, v)) {
			return false
		}
	}
	return true
}

//

type MutStdMap[K comparable, V any] struct {
	m StdMap[K, V]
}

func NewMutStdMap[K comparable, V any](it bt.Iterable[bt.Kv[K, V]]) *MutStdMap[K, V] {
	return &MutStdMap[K, V]{m: NewStdMap[K, V](it)}
}

func WrapMap[K comparable, V any](m map[K]V) *MutStdMap[K, V] {
	return &MutStdMap[K, V]{StdMap[K, V]{m}}
}

var _ MutMap[int, any] = &MutStdMap[int, any]{}

func (m *MutStdMap[K, V]) isMut() {}

func (m *MutStdMap[K, V]) Len() int                               { return m.m.Len() }
func (m *MutStdMap[K, V]) Contains(k K) bool                      { return m.m.Contains(k) }
func (m *MutStdMap[K, V]) Get(k K) V                              { return m.m.Get(k) }
func (m *MutStdMap[K, V]) TryGet(k K) (V, bool)                   { return m.m.TryGet(k) }
func (m *MutStdMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]]      { return m.m.Iterate() }
func (m *MutStdMap[K, V]) ForEach(fn func(bt.Kv[K, V]) bool) bool { return m.m.ForEach(fn) }

func (m *MutStdMap[K, V]) lazyInit() {
	if m.m.m == nil {
		m.m.m = make(map[K]V)
	}
}

func (m *MutStdMap[K, V]) Put(k K, v V) {
	m.lazyInit()
	m.m.m[k] = v
}

func (m *MutStdMap[K, V]) Delete(k K) {
	m.lazyInit()
	delete(m.m.m, k)
}

func (m *MutStdMap[K, V]) Default(k K, v V) bool {
	m.lazyInit()
	if m.Contains(k) {
		return false
	}
	m.m.m[k] = v
	return true
}

var _ Decay[Map[int, string]] = &MutStdMap[int, string]{}

func (m *MutStdMap[K, V]) Decay() Map[K, V] { return &m.m }
