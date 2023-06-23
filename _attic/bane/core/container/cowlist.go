package container

import (
	"sync"
	"sync/atomic"

	its "github.com/wrmsr/bane/core/iterators"
	"github.com/wrmsr/bane/core/slices"
	bt "github.com/wrmsr/bane/core/types"
)

type CowList[T any] struct {
	mtx sync.Mutex
	r   atomic.Value
}

func NewCowList[T any](it bt.Iterable[T]) *CowList[T] {
	l := &CowList[T]{}
	if it != nil {
		l.r.Store(its.Seq(it))
	}
	return l
}

func NewCowListOf[T any](vs ...T) *CowList[T] {
	return NewCowList(its.Of(vs...))
}

func (m *CowList[T]) get() []T {
	if r := m.r.Load(); r != nil {
		return r.([]T)
	}
	return nil
}

func (m *CowList[T]) Clone() *CowList[T] {
	r := &CowList[T]{}
	if v := m.r.Load(); v != nil {
		r.r.Store(v)
	}
	return r
}

var _ SyncMutList[int] = &CowList[int]{}

func (m *CowList[T]) isMut()  {}
func (m *CowList[T]) isSync() {}

func (m *CowList[T]) Len() int {
	return len(m.get())
}

func (m *CowList[T]) Get(i int) T {
	return m.get()[i]
}

func (m *CowList[T]) Iterate() bt.Iterator[T] {
	return its.OfSlice(m.get()).Iterate()
}

func (m *CowList[T]) ForEach(fn func(v T) bool) bool {
	for _, v := range m.get() {
		if !fn(v) {
			return false
		}
	}
	return true
}

func (m *CowList[T]) mut(fn func([]T) []T) {
	m.mtx.Lock()
	defer m.mtx.Unlock()

	m.r.Store(fn(slices.Clone(m.get())))
}

func (m *CowList[T]) Put(i int, v T) {
	m.mut(func(s []T) []T {
		s[i] = v
		return s
	})
}

func (m *CowList[T]) Append(v T) {
	m.mut(func(s []T) []T {
		return append(s, v)
	})
}

func (m *CowList[T]) Delete(i int) {
	m.mut(func(s []T) []T {
		return append(s[:i], s[i+1:]...)
	})
}
