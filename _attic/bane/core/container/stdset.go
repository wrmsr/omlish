package container

import (
	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

//

type StdSet[T comparable] struct {
	m map[T]struct{}
}

func NewStdSet[T comparable](it bt.Iterable[T]) StdSet[T] {
	s := StdSet[T]{}
	if it != nil {
		m := make(map[T]struct{})
		for it := it.Iterate(); it.HasNext(); {
			m[it.Next()] = struct{}{}
		}
		s.m = m
	}
	return s
}

func NewStdSetOf[T comparable](vs ...T) StdSet[T] {
	return NewStdSet(its.Of(vs...))
}

var _ Set[int] = StdSet[int]{}

func (s StdSet[T]) Len() int {
	if s.m == nil {
		return 0
	}
	return len(s.m)
}

func (s StdSet[T]) Contains(t T) bool {
	if s.m == nil {
		return false
	}
	_, ok := s.m[t]
	return ok
}

func (s StdSet[T]) Iterate() bt.Iterator[T] {
	if s.m == nil {
		return its.Empty[T]().Iterate()
	}
	return its.Map(its.OfMap(s.m), func(kv bt.Kv[T, struct{}]) T { return kv.K }).Iterate()
}

func (s StdSet[T]) ForEach(fn func(T) bool) bool {
	if s.m == nil {
		return true
	}
	for v := range s.m {
		if !fn(v) {
			return false
		}
	}
	return true
}

//

type MutStdSet[T comparable] struct {
	s StdSet[T]
}

func NewMutStdSet[T comparable](it bt.Iterable[T]) *MutStdSet[T] {
	return &MutStdSet[T]{s: NewStdSet(it)}
}

func NewMutStdSetOf[T comparable](vs ...T) *MutStdSet[T] {
	return NewMutStdSet(its.Of(vs...))
}

func WrapSet[T comparable](s map[T]struct{}) *MutStdSet[T] {
	return &MutStdSet[T]{StdSet[T]{s}}
}

var _ MutSet[int] = &MutStdSet[int]{}

func (s *MutStdSet[T]) isMut() {}

func (s *MutStdSet[T]) Len() int                       { return s.s.Len() }
func (s *MutStdSet[T]) Contains(v T) bool              { return s.s.Contains(v) }
func (s *MutStdSet[T]) Iterate() bt.Iterator[T]        { return s.s.Iterate() }
func (s *MutStdSet[T]) ForEach(fn func(v T) bool) bool { return s.s.ForEach(fn) }

func (s *MutStdSet[T]) lazyInit() {
	if s.s.m == nil {
		s.s.m = make(map[T]struct{})
	}
}

func (s *MutStdSet[T]) Add(value T) {
	s.s.m[value] = struct{}{}
}

func (s *MutStdSet[T]) TryAdd(value T) bool {
	if s.Contains(value) {
		return false
	}
	s.s.m[value] = struct{}{}
	return true
}

func (s *MutStdSet[T]) Remove(value T) {
	delete(s.s.m, value)
}

func (s *MutStdSet[T]) TryRemove(value T) bool {
	if s.Contains(value) {
		return false
	}
	delete(s.s.m, value)
	return true
}

var _ Decay[Set[int]] = &MutStdSet[int]{}

func (s *MutStdSet[T]) Decay() Set[T] { return s.s }
