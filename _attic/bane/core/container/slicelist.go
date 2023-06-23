package container

import (
	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

//

type SliceList[T any] struct {
	s []T
}

func NewSliceList[T any](it bt.Iterable[T]) SliceList[T] {
	s := SliceList[T]{}
	if it != nil {
		for it := it.Iterate(); it.HasNext(); {
			s.s = append(s.s, it.Next())
		}
	}
	return s
}

func NewSliceListOf[T any](vs ...T) SliceList[T] {
	return NewSliceList(its.Of(vs...))
}

var _ List[int] = SliceList[int]{}

func (l SliceList[T]) Len() int {
	return len(l.s)
}

func (l SliceList[T]) Get(i int) T {
	return l.s[i]
}

func (l SliceList[T]) Iterate() bt.Iterator[T] {
	return its.OfSlice(l.s).Iterate()
}

func (l SliceList[T]) ForEach(fn func(v T) bool) bool {
	for _, v := range l.s {
		if !fn(v) {
			return false
		}
	}
	return true
}

//

type MutSliceList[T any] struct {
	l SliceList[T]
}

func NewMutSliceList[T any](it bt.Iterable[T]) *MutSliceList[T] {
	return &MutSliceList[T]{l: NewSliceList(it)}
}

func NewMutSliceListOf[T any](vs ...T) *MutSliceList[T] {
	return NewMutSliceList(its.Of(vs...))
}

func WrapSlice[T any](s []T) MutList[T] {
	return &MutSliceList[T]{SliceList[T]{s}}
}

var _ MutList[int] = &MutSliceList[int]{}

func (l *MutSliceList[T]) isMut() {}

func (l *MutSliceList[T]) Len() int                       { return l.l.Len() }
func (l *MutSliceList[T]) Get(i int) T                    { return l.l.Get(i) }
func (l *MutSliceList[T]) Iterate() bt.Iterator[T]        { return l.l.Iterate() }
func (l *MutSliceList[T]) ForEach(fn func(v T) bool) bool { return l.l.ForEach(fn) }

func (l *MutSliceList[T]) Put(i int, v T) {
	l.l.s[i] = v
}

func (l *MutSliceList[T]) Append(v T) {
	l.l.s = append(l.l.s, v)
}

func (l *MutSliceList[T]) Delete(i int) {
	l.l.s = append(l.l.s[:i], l.l.s[i+1:]...)
}

var _ Decay[List[int]] = &MutSliceList[int]{}

func (l *MutSliceList[T]) Decay() List[T] { return l.l }
