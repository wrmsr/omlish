package container

import (
	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

//

type ListView[F, T any] struct {
	l  List[F]
	fn func(F) T
}

func NewListView[F, T any](l List[F], fn func(F) T) ListView[F, T] {
	return ListView[F, T]{l: l, fn: fn}
}

var _ List[string] = ListView[int, string]{}

func (l ListView[F, T]) Len() int    { return l.l.Len() }
func (l ListView[F, T]) Get(i int) T { return l.fn(l.l.Get(i)) }

func (l ListView[F, T]) Iterate() bt.Iterator[T] {
	return its.Map[F, T](l.l, l.fn).Iterate()
}

func (l ListView[F, T]) ForEach(fn func(v T) bool) bool {
	return l.l.ForEach(func(f F) bool { return fn(l.fn(f)) })
}

//

type SetView[F, T any] struct {
	s   Set[F]
	bfn bt.BiFunc[F, T]
}

func NewSetView[F, T any](s Set[F], bfn bt.BiFunc[F, T]) SetView[F, T] {
	return SetView[F, T]{s: s, bfn: bfn}
}

var _ Set[string] = SetView[int, string]{}

func (s SetView[F, T]) Len() int          { return s.s.Len() }
func (s SetView[F, T]) Contains(v T) bool { return s.s.Contains(s.bfn.Flip().Call(v)) }

func (s SetView[F, T]) Iterate() bt.Iterator[T] {
	return its.Map[F, T](s.s, s.bfn.Call).Iterate()
}

func (s SetView[F, T]) ForEach(fn func(v T) bool) bool {
	return s.s.ForEach(func(f F) bool { return fn(s.bfn.Call(f)) })
}

//

type MapView[K comparable, VF, VT any] struct {
	m  Map[K, VF]
	fn func(VF) VT
}

func NewMapView[K comparable, VF, VT any](m Map[K, VF], fn func(VF) VT) MapView[K, VF, VT] {
	return MapView[K, VF, VT]{m: m, fn: fn}
}

var _ Map[int, string] = MapView[int, uint, string]{}

func (m MapView[K, VF, VT]) Len() int          { return m.m.Len() }
func (m MapView[K, VF, VT]) Contains(k K) bool { return m.m.Contains(k) }
func (m MapView[K, VF, VT]) Get(k K) VT        { return m.fn(m.m.Get(k)) }

func (m MapView[K, VF, VT]) TryGet(k K) (VT, bool) {
	v, ok := m.m.TryGet(k)
	if ok {
		return m.fn(v), true
	}
	var z VT
	return z, false
}

func (m MapView[K, VF, VT]) Iterate() bt.Iterator[bt.Kv[K, VT]] {
	return its.MapValues[K, VF, VT](m.m, m.fn).Iterate()
}

func (m MapView[K, VF, VT]) ForEach(fn func(v bt.Kv[K, VT]) bool) bool {
	return m.m.ForEach(func(kv bt.Kv[K, VF]) bool { return fn(bt.KvOf(kv.K, m.fn(kv.V))) })
}
