package container

import (
	bt "github.com/wrmsr/bane/core/types"
)

//

type SimpleBiMap[K, V comparable] struct {
	Map[K, V]
	i Map[V, K]
}

func initBiMap[K, V comparable](it bt.Iterable[bt.Kv[K, V]]) (map[K]V, map[V]K) {
	m := make(map[K]V)
	i := make(map[V]K)
	if it != nil {
		for it := it.Iterate(); it.HasNext(); {
			kv := it.Next()
			m[kv.K] = kv.V
			i[kv.V] = kv.K
		}
	}
	return m, i
}

func NewSimpleBiMap[K, V comparable](it bt.Iterable[bt.Kv[K, V]]) SimpleBiMap[K, V] {
	m, i := initBiMap(it)
	return SimpleBiMap[K, V]{Map: StdMap[K, V]{m: m}, i: StdMap[V, K]{i}}
}

var _ BiMap[int, string] = SimpleBiMap[int, string]{}

func (m SimpleBiMap[K, V]) Invert() BiMap[V, K] {
	var r any = SimpleBiMap[V, K]{Map: m.i, i: m.Map}
	return r.(BiMap[V, K]) // FIXME: goland bug
}

//

type MutSimpleBiMap[K, V comparable] struct {
	m MutMap[K, V]
	i MutMap[V, K]
}

func NewMutSimpleBiMap[K, V comparable](it bt.Iterable[bt.Kv[K, V]]) MutSimpleBiMap[K, V] {
	m, i := initBiMap(it)
	return MutSimpleBiMap[K, V]{
		m: &MutStdMap[K, V]{StdMap[K, V]{m: m}},
		i: &MutStdMap[V, K]{StdMap[V, K]{i}},
	}
}

var _ MutBiMap[int, string] = MutSimpleBiMap[int, string]{}

func (m MutSimpleBiMap[K, V]) isMut() {}

func (m MutSimpleBiMap[K, V]) Len() int                                  { return m.m.Len() }
func (m MutSimpleBiMap[K, V]) Contains(k K) bool                         { return m.m.Contains(k) }
func (m MutSimpleBiMap[K, V]) Get(k K) V                                 { return m.m.Get(k) }
func (m MutSimpleBiMap[K, V]) TryGet(k K) (V, bool)                      { return m.m.TryGet(k) }
func (m MutSimpleBiMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]]         { return m.m.Iterate() }
func (m MutSimpleBiMap[K, V]) ForEach(fn func(kv bt.Kv[K, V]) bool) bool { return m.m.ForEach(fn) }

func (m MutSimpleBiMap[K, V]) Put(k K, v V) {
	if o, ok := m.m.TryGet(k); ok {
		m.m.Delete(k)
		m.i.Delete(o)
	}
	if o, ok := m.i.TryGet(v); ok {
		m.m.Delete(o)
		m.i.Delete(v)
	}
	m.m.Put(k, v)
	m.i.Put(v, k)
}

func (m MutSimpleBiMap[K, V]) Delete(k K) {
	if o, ok := m.TryGet(k); ok {
		m.m.Delete(k)
		m.i.Delete(o)
	}
}

func (m MutSimpleBiMap[K, V]) Default(k K, v V) bool {
	if m.Contains(k) {
		return false
	}
	m.Put(k, v)
	return true
}

func (m MutSimpleBiMap[K, V]) Invert() BiMap[V, K] {
	return m.MutInvert()
}

func (m MutSimpleBiMap[K, V]) MutInvert() MutBiMap[V, K] {
	var r any = MutSimpleBiMap[V, K]{m: m.i, i: m.m}
	return r.(MutBiMap[V, K]) // FIXME: goland bug
}
