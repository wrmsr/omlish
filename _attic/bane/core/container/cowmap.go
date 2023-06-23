package container

import (
	"sync"
	"sync/atomic"

	its "github.com/wrmsr/bane/core/iterators"
	"github.com/wrmsr/bane/core/maps"
	bt "github.com/wrmsr/bane/core/types"
)

//

type CowMap[K comparable, V any] struct {
	mtx sync.Mutex
	r   atomic.Value
}

func NewCowMap[K comparable, V any](it bt.Iterable[bt.Kv[K, V]]) *CowMap[K, V] {
	cm := &CowMap[K, V]{}
	if it != nil {
		m := make(map[K]V)
		for it := it.Iterate(); it.HasNext(); {
			c := it.Next()
			m[c.K] = c.V
		}
		cm.r.Store(m)
	}
	return cm
}

func (m *CowMap[K, V]) get() map[K]V {
	if r := m.r.Load(); r != nil {
		return r.(map[K]V)
	}
	return nil
}

func (m *CowMap[K, V]) Clone() *CowMap[K, V] {
	r := &CowMap[K, V]{}
	if v := m.r.Load(); v != nil {
		r.r.Store(v)
	}
	return r
}

var _ SyncMutMap[int, any] = &CowMap[int, any]{}

func (m *CowMap[K, V]) isMut()  {}
func (m *CowMap[K, V]) isSync() {}

func (m *CowMap[K, V]) Len() int {
	r := m.get()
	if r == nil {
		return 0
	}
	return len(r)
}

func (m *CowMap[K, V]) Contains(k K) bool {
	r := m.get()
	if r == nil {
		return false
	}
	_, ok := r[k]
	return ok
}

func (m *CowMap[K, V]) Get(k K) V {
	r := m.get()
	if r == nil {
		var z V
		return z
	}
	return r[k]
}

func (m *CowMap[K, V]) TryGet(k K) (V, bool) {
	r := m.get()
	if r == nil {
		var z V
		return z, false
	}
	v, ok := r[k]
	return v, ok
}

func (m *CowMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	r := m.get()
	if r == nil {
		return its.Empty[bt.Kv[K, V]]().Iterate()
	}
	return its.OfMap[K, V](r).Iterate()
}

func (m *CowMap[K, V]) ForEach(fn func(bt.Kv[K, V]) bool) bool {
	r := m.get()
	if r == nil {
		return true
	}
	for k, v := range r {
		if !fn(bt.KvOf(k, v)) {
			return false
		}
	}
	return true
}

func (m *CowMap[K, V]) mut(fn func(map[K]V)) {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	r := m.get()
	if r == nil {
		r = make(map[K]V)
	}
	nm := maps.Clone(r)
	fn(nm)
	m.r.Store(nm)
}

func (m *CowMap[K, V]) Put(k K, v V) {
	m.mut(func(m map[K]V) {
		m[k] = v
	})
}

func (m *CowMap[K, V]) Delete(k K) {
	m.mut(func(m map[K]V) {
		delete(m, k)
	})
}

func (m *CowMap[K, V]) Default(k K, v V) bool {
	var r bool
	m.mut(func(m map[K]V) {
		if _, ok := m[k]; !ok {
			m[k] = v
			r = true
		}
	})
	return r
}
