package container

import (
	"errors"

	its "github.com/wrmsr/bane/core/iterators"
	"github.com/wrmsr/bane/core/slices"
	bt "github.com/wrmsr/bane/core/types"
)

//

type MapShape[K comparable] struct {
	ks []K
	m  map[K]int
}

func NewMapShape[K comparable](ks bt.Iterable[K]) MapShape[K] {
	var s []K
	m := make(map[K]int)
	i := 0
	for it := ks.Iterate(); it.HasNext(); {
		k := it.Next()
		if _, ok := m[k]; ok {
			panic(KeyError[K]{k})
		}
		s = append(s, k)
		m[k] = i
		i++
	}
	return MapShape[K]{
		ks: s,
		m:  m,
	}
}

var _ Set[int] = MapShape[int]{}

func (s MapShape[K]) Len() int {
	return len(s.ks)
}

func (s MapShape[K]) Contains(k K) bool {
	_, ok := s.m[k]
	return ok
}

func (s MapShape[K]) Iterate() bt.Iterator[K] {
	return its.OfSlice(s.ks).Iterate()
}

func (s MapShape[K]) ForEach(fn func(v K) bool) bool {
	for _, k := range s.ks {
		if !fn(k) {
			return false
		}
	}
	return true
}

//

type ShapeMap[K comparable, V any] struct {
	shape MapShape[K]
	vs    []V
}

func NewShapeMap[K comparable, V any](shape MapShape[K], vs bt.Iterable[V]) ShapeMap[K, V] {
	s := make([]V, 0, shape.Len())
	if vs != nil {
		i := 0
		for it := vs.Iterate(); it.HasNext(); {
			s[i] = it.Next()
			i++
		}
		if i != shape.Len() {
			panic(errors.New("length mismatch"))
		}
	}
	return ShapeMap[K, V]{
		shape: shape,
		vs:    s,
	}
}

func NewShapeMapFromSlice[K comparable, V any](shape MapShape[K], s []V) ShapeMap[K, V] {
	if len(s) != shape.Len() {
		panic(errors.New("length mismatch"))
	}
	return ShapeMap[K, V]{
		shape: shape,
		vs:    s,
	}
}

func (m ShapeMap[K, V]) Shape() MapShape[K] { return m.shape }

func (m ShapeMap[K, V]) Values() []V   { return slices.Clone(m.vs) }
func (m ShapeMap[K, V]) Value(i int) V { return m.vs[i] }

func (m ShapeMap[K, V]) Clone() ShapeMap[K, V] {
	return ShapeMap[K, V]{shape: m.shape, vs: slices.Clone(m.vs)}
}

var _ Map[int, string] = ShapeMap[int, string]{}

func (m ShapeMap[K, V]) Len() int {
	return len(m.vs)
}

func (m ShapeMap[K, V]) Contains(k K) bool {
	return m.shape.Contains(k)
}

func (m ShapeMap[K, V]) Get(k K) V {
	v, _ := m.TryGet(k)
	return v
}

func (m ShapeMap[K, V]) TryGet(k K) (V, bool) {
	if i, ok := m.shape.m[k]; ok {
		return m.vs[i], true
	}
	var z V
	return z, false
}

func (m ShapeMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]] {
	return its.Map(its.Range(0, m.shape.Len(), 1), func(i int) bt.Kv[K, V] {
		return bt.KvOf(m.shape.ks[i], m.vs[i])
	}).Iterate()
}

func (m ShapeMap[K, V]) ForEach(fn func(kv bt.Kv[K, V]) bool) bool {
	for i, v := range m.vs {
		if !fn(bt.KvOf(m.shape.ks[i], v)) {
			return false
		}
	}
	return true
}

//

type MutShapeMap[K comparable, V any] struct {
	m ShapeMap[K, V]
}

func NewMutShapeMap[K comparable, V any](shape MapShape[K], vs bt.Iterable[V]) MutShapeMap[K, V] {
	return MutShapeMap[K, V]{m: NewShapeMap(shape, vs)}
}

func (m MutShapeMap[K, V]) Shape() MapShape[K] { return m.m.shape }

func (m MutShapeMap[K, V]) Values() []V    { return m.m.vs }
func (m MutShapeMap[K, V]) Value(i int) *V { return &m.m.vs[i] }

var _ MutMap[int, string] = MutShapeMap[int, string]{}

func (m MutShapeMap[K, V]) isMut() {}

func (m MutShapeMap[K, V]) Len() int                                  { return m.m.Len() }
func (m MutShapeMap[K, V]) Contains(k K) bool                         { return m.m.Contains(k) }
func (m MutShapeMap[K, V]) Get(k K) V                                 { return m.m.Get(k) }
func (m MutShapeMap[K, V]) TryGet(k K) (V, bool)                      { return m.m.TryGet(k) }
func (m MutShapeMap[K, V]) Iterate() bt.Iterator[bt.Kv[K, V]]         { return m.m.Iterate() }
func (m MutShapeMap[K, V]) ForEach(fn func(kv bt.Kv[K, V]) bool) bool { return m.m.ForEach(fn) }

func (m MutShapeMap[K, V]) Put(k K, v V) {
	if i, ok := m.m.shape.m[k]; ok {
		m.m.vs[i] = v
		return
	}
	panic(KeyError[K]{k})
}

func (m MutShapeMap[K, V]) Delete(k K) {
	var z V
	m.Put(k, z)
}

func (m MutShapeMap[K, V]) Default(k K, v V) bool {
	return false
}
