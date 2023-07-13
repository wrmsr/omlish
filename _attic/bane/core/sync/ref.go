package sync

import (
	"sync"

	bt "github.com/wrmsr/bane/core/types"
)

//

type Ref[T any] interface {
	Acquire() bt.Optional[T]
	Release()

	AddCallback(cb func(r Ref[T], v T))
}

//

type ref[T any] struct {
	v bt.Optional[T]
	c int32

	cbs []func(r Ref[T], v T)
}

func NewRef[T any](v T) Ref[T] {
	return &ref[T]{v: bt.Just(v), c: 1}
}

var _ Ref[int] = &ref[int]{}

func (r *ref[T]) Acquire() bt.Optional[T] {
	if r.v.Present() {
		r.c++
	}

	return r.v
}

func (r *ref[T]) Release() {
	r.c--
	if r.c < 0 {
		panic("negative refs")
	}

	if r.c == 0 {
		if !r.v.Present() {
			panic("broken ref")
		}

		v := r.v.Value()
		for _, cb := range r.cbs {
			cb(r, v)
		}

		if r.c < 0 {
			panic("negative refs")
		}

		if r.c == 0 {
			r.v = bt.None[T]()
		}
	}
}

func (r *ref[T]) AddCallback(cb func(r Ref[T], v T)) {
	r.cbs = append(r.cbs, cb)
}

//

type syncRef[T any] struct {
	mtx sync.Mutex

	r ref[T]
}

func NewSyncRef[T any](v T) Ref[T] {
	return &syncRef[T]{r: ref[T]{v: bt.Just(v), c: 1}}
}

var _ Ref[int] = &syncRef[int]{}

func (r *syncRef[T]) Acquire() bt.Optional[T] {
	r.mtx.Lock()
	defer r.mtx.Unlock()

	return r.r.Acquire()
}

func (r *syncRef[T]) Release() {
	r.mtx.Lock()
	defer r.mtx.Unlock()

	r.r.Release()
}

func (r *syncRef[T]) AddCallback(cb func(r Ref[T], v T)) {
	r.mtx.Lock()
	defer r.mtx.Unlock()

	r.r.AddCallback(cb)
}
