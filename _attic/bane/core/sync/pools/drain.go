package pools

import (
	"reflect"
	"sync"
	"sync/atomic"
)

type AnyDrainPool interface {
	Type() reflect.Type
	Stats() DrainPoolStats
	Drain() int
}

type DrainPoolStats struct {
	New, Put, Get, Drain int64
}

type DrainPool[T any] struct {
	o sync.Pool

	s DrainPoolStats
}

func NewDrainPool[T any](fn func() T) *DrainPool[T] {
	p := &DrainPool[T]{}
	p.o.New = func() any {
		atomic.AddInt64(&p.s.New, 1)
		return fn()
	}
	return p
}

var _ AnyDrainPool = &DrainPool[int]{}

func (p *DrainPool[T]) Type() reflect.Type {
	var z T
	return reflect.TypeOf(z)
}

var _ Pool[int] = &DrainPool[int]{}

func (p *DrainPool[T]) Put(x T) {
	atomic.AddInt64(&p.s.Put, 1)
	p.o.Put(x)
}

func (p *DrainPool[T]) Get() T {
	atomic.AddInt64(&p.s.Get, 1)
	return p.o.Get().(T)
}

func (p *DrainPool[T]) Stats() DrainPoolStats {
	return p.s
}

func (p *DrainPool[T]) Drain() int {
	i := 0
	for c := atomic.LoadInt64(&p.s.New); c == atomic.LoadInt64(&p.s.New); i++ {
		p.o.Get()
	}
	atomic.AddInt64(&p.s.Drain, int64(i))
	return i
}
