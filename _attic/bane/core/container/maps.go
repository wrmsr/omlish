package container

import (
	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

func Keys[K, V any](m Map[K, V]) bt.Iterable[K] {
	return its.Keys[K, V](m)
}

func Values[K, V any](m Map[K, V]) bt.Iterable[V] {
	return its.Values[K, V](m)
}

func MapKeys[KF, KT comparable, V any](fn func(k KF) KT, m Map[KF, V]) Map[KT, V] {
	r := NewMutStdMap[KT, V](nil)
	m.ForEach(func(kv bt.Kv[KF, V]) bool {
		r.Put(fn(kv.K), kv.V)
		return true
	})
	return r
}

func MapValues[K comparable, VF, VT any](fn func(v VF) VT, m Map[K, VF]) Map[K, VT] {
	r := NewMutStdMap[K, VT](nil)
	m.ForEach(func(kv bt.Kv[K, VF]) bool {
		r.Put(kv.K, fn(kv.V))
		return true
	})
	return r
}

//func NewListMap[K comparable, V any](it its.Iterable[bt.Kv[K, V]]) Map[K, List[V]] {
//	m := NewMutStdMap[K, MutList[V]](nil)
//	for it := it.Iterate(); it.HasNext(); {
//		kv := it.Next()
//		if l, ok := m.TryGet(kv.K); ok {
//			l.Append(kv.V)
//		} else {
//			m.Put(kv.K, NewMutListOf(kv.V))
//		}
//	}
//	return m.(Map[K, List[V]])
//}

//func NewSetMap[K, V comparable](it its.Iterable[bt.Kv[K, V]]) Map[K, Set[V]] {
//	m := NewMutStdMap[K, MutSet[V]](nil)
//	for it := it.Iterate(); it.HasNext(); {
//		kv := it.Next()
//		if s, ok := m.TryGet(kv.K); ok {
//			s.Add(kv.V)
//		} else {
//			m.Put(kv.K, NewMutSetOf(kv.V))
//		}
//	}
//	return m.(Map[K, Set[V]])
//}

func GetOrMake[K, V any](m MutMap[K, V], k K, fn func() V) V {
	v, ok := m.TryGet(k)
	if ok {
		return v
	}
	v = fn()
	m.Put(k, v)
	return v
}
