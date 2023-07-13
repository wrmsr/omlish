package pools

import (
	"sync"
)

//

type Pool[T any] interface {
	Get() T
	Put(x T)
}

//

type WrappedSyncPool[T any] struct {
	o *sync.Pool
}

func WrapSyncPool[T any](o *sync.Pool) WrappedSyncPool[T] {
	return WrappedSyncPool[T]{o: o}
}

var _ Pool[int] = WrappedSyncPool[int]{}

func (p WrappedSyncPool[T]) Get() T {
	return p.o.Get().(T)
}

func (p WrappedSyncPool[T]) Put(x T) {
	p.o.Put(x)
}

//

type SyncPool[T any] struct {
	o sync.Pool
}

func NewSyncPool[T any](fn func() T) *SyncPool[T] {
	return &SyncPool[T]{o: sync.Pool{New: func() any { return fn() }}}
}

var _ Pool[int] = &SyncPool[int]{}

func (p *SyncPool[T]) Get() T {
	return p.o.Get().(T)
}

func (p *SyncPool[T]) Put(x T) {
	p.o.Put(x)
}

//

type StubPool[T any] struct {
	New func() T
}

var _ Pool[int] = StubPool[int]{}

func (p StubPool[T]) Get() T {
	return p.New()
}

func (p StubPool[T]) Put(x T) {}
