package sync

import (
	"sync"
	"sync/atomic"
)

//

type Lazy[T any] struct {
	once sync.Once

	v T
}

func (va *Lazy[T]) Set(v T) bool {
	ret := false
	va.once.Do(func() {
		va.v = v
		ret = true
	})
	return ret
}

func (va *Lazy[T]) Get(fn func() T) T {
	va.once.Do(func() {
		va.v = fn()
	})
	return va.v
}

//

type box[T any] struct {
	v T
}

type LazyFn[T any] struct {
	Fn func() T

	o sync.Once
	v atomic.Value
}

func NewLazyFn[T any](fn func() T) *LazyFn[T] {
	return &LazyFn[T]{
		Fn: fn,
	}
}

func (l *LazyFn[T]) Peek() (T, bool) {
	if b := l.v.Load(); b != nil {
		return b.(box[T]).v, true
	}
	var z T
	return z, false
}

func (l *LazyFn[T]) Get() T {
	l.o.Do(func() {
		if _, ok := l.Peek(); !ok {
			l.Set(l.Fn())
		}
	})
	v, ok := l.Peek()
	if !ok {
		panic("unreachable")
	}
	return v
}

func (l *LazyFn[T]) Set(v T) T {
	l.v.Store(box[T]{v})
	return v
}
