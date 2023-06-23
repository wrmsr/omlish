package container

import (
	"sync"

	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

//

type locked struct {
	mtx sync.Mutex
}

var _ Sync = &locked{}

func (l *locked) isSync() {}

//

type LockedMap[K, V any] struct {
	locked
	m Map[K, V]
}

func NewLockedMap[K, V any](m Map[K, V]) *LockedMap[K, V] {
	return &LockedMap[K, V]{m: m}
}

var _ SyncMap[int, string] = &LockedMap[int, string]{}

func (m *LockedMap[K, V]) Len() int {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	return m.m.Len()
}

func (m *LockedMap[K, V]) Contains(k K) bool {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	return m.m.Contains(k)
}

func (m *LockedMap[K, V]) Get(k K) V {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	return m.m.Get(k)
}

func (m *LockedMap[K, V]) TryGet(k K) (V, bool) {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	return m.m.TryGet(k)
}

func (m *LockedMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	return its.OfSlice(its.Seq[bt.Kv[K, V]](m.m)).Iterate()
}

func (m *LockedMap[K, V]) ForEach(fn func(v bt.Kv[K, V]) bool) bool {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	return m.m.ForEach(fn)
}

//

type LockedMutMap[K, V any] struct {
	LockedMap[K, V]
	m MutMap[K, V]
}

func NewLockedMutMap[K, V any](m MutMap[K, V]) *LockedMutMap[K, V] {
	return &LockedMutMap[K, V]{LockedMap: LockedMap[K, V]{m: m}, m: m}
}

var _ SyncMutMap[int, string] = &LockedMutMap[int, string]{}

func (m *LockedMutMap[K, V]) isMut() {}

func (m *LockedMutMap[K, V]) Put(k K, v V) {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	m.m.Put(k, v)
}

func (m *LockedMutMap[K, V]) Delete(k K) {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	m.m.Delete(k)
}

func (m *LockedMutMap[K, V]) Default(k K, v V) bool {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	return m.m.Default(k, v)
}
