package container

import bt "github.com/wrmsr/bane/core/types"

//

type DenseList8[T any] struct {
	a [8]T
	s []T
	l int
}

var _ List[int] = DenseList8[int]{}

func (l DenseList8[T]) Len() int {
	return l.l
}

func (l DenseList8[T]) Get(i int) T {
	if i >= l.l {
		panic("index out of range")
	}
	if i < 8 {
		return l.a[i]
	}
	return l.s[i-8]
}

type denseList8Iterator[T any] struct {
	l DenseList8[T]
	n int
}

var _ bt.Iterator[int] = &denseList8Iterator[int]{}

func (i denseList8Iterator[T]) Iterate() bt.Iterator[T] {
	return i
}

func (i denseList8Iterator[T]) HasNext() bool {
	return i.n < i.l.l
}

func (i denseList8Iterator[T]) Next() T {
	if i.n >= i.l.l {
		panic(bt.IteratorExhaustedError{})
	}
	n := i.n
	i.n++
	if i.n < 8 {
		return i.l.a[n]
	}
	return i.l.s[n-8]
}

func (l DenseList8[T]) Iterate() bt.Iterator[T] {
	return &denseList8Iterator[T]{l: l}
}

func (l DenseList8[T]) ForEach(fn func(v T) bool) bool {
	for i := 0; i < l.l; i++ {
		if !fn(l.a[i]) {
			return false
		}
	}
	for i := 8; i < l.l; i++ {
		if !fn(l.s[i-8]) {
			return false
		}
	}
	return true
}

//

type MutDenseList8[T any] struct {
	l DenseList8[T]
}

var _ MutList[int] = &MutDenseList8[int]{}

func (l *MutDenseList8[T]) isMut() {}

func (l *MutDenseList8[T]) Len() int                       { return l.l.Len() }
func (l *MutDenseList8[T]) Get(i int) T                    { return l.l.Get(i) }
func (l *MutDenseList8[T]) Iterate() bt.Iterator[T]        { return l.l.Iterate() }
func (l *MutDenseList8[T]) ForEach(fn func(v T) bool) bool { return l.l.ForEach(fn) }

func (l *MutDenseList8[T]) Put(i int, v T) {
	if i < 0 || i > l.l.l {
		panic("index ouf of range")
	}
	if i < 8 {
		l.l.a[i] = v
	} else {
		l.l.s[i-8] = v
	}
}

func (l *MutDenseList8[T]) Append(v T) {
	if l.l.l < 8 {
		l.l.a[l.l.l] = v
	} else {
		l.l.s = append(l.l.s, v)
	}
	l.l.l++
}

func (l *MutDenseList8[T]) Delete(i int) {
	panic("implement me")
}
