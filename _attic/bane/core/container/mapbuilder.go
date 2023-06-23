/*
See also maps/builder.go
*/
package container

import (
	bt "github.com/wrmsr/bane/core/types"
)

type MapBuilder[K comparable, V any] struct {
	m *SliceMap[K, V]
}

func NewMapBuilder[K comparable, V any]() *MapBuilder[K, V] {
	return &MapBuilder[K, V]{
		m: &SliceMap[K, V]{
			m: make(map[K]int),
		},
	}
}

func (b *MapBuilder[K, V]) Put(k K, v V) *MapBuilder[K, V] {
	b.m.put(k, v)
	return b
}

func (b *MapBuilder[K, V]) Update(it bt.Iterable[bt.Kv[K, V]]) *MapBuilder[K, V] {
	if it != nil {
		for it := it.Iterate(); it.HasNext(); {
			kv := it.Next()
			b.m.put(kv.K, kv.V)
		}
	}
	return b
}

func (b *MapBuilder[K, V]) Filter(fn func(kv bt.Kv[K, V]) bool) *MapBuilder[K, V] {
	b.m.filter(fn)
	return b
}

func (b *MapBuilder[K, V]) FilterKeys(fn func(k K) bool) *MapBuilder[K, V] {
	b.m.filter(func(kv bt.Kv[K, V]) bool { return fn(kv.K) })
	return b
}

func (b *MapBuilder[K, V]) FilterValues(fn func(v V) bool) *MapBuilder[K, V] {
	b.m.filter(func(kv bt.Kv[K, V]) bool { return fn(kv.V) })
	return b
}

func (b *MapBuilder[K, V]) Delete(k K) *MapBuilder[K, V] {
	b.m.delete(k)
	return b
}

func (b *MapBuilder[K, V]) Default(k K, v V) *MapBuilder[K, V] {
	b.m.default_(k, v)
	return b
}

func (b *MapBuilder[K, V]) Build() OrderedMap[K, V] {
	r := b.m
	b.m = nil
	return r
}
