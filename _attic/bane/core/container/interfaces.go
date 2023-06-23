package container

import (
	bt "github.com/wrmsr/bane/core/types"
)

//

type Sync interface {
	isSync()
}

type Mut interface {
	isMut()
}

type Ordered[T any] interface {
	isOrdered()

	bt.Iterable[T]
}

type Persistent[T any] interface {
	isPersistent()

	bt.Iterable[T]
}

type Sorted[A, I any] interface {
	isSorted()

	bt.Iterable[I]
	ReverseIterate() bt.Iterator[I]

	IterateFrom(a A) bt.Iterator[I]
	ReverseIterateFrom(a A) bt.Iterator[I]
}

//

type List[T any] interface {
	Len() int
	Get(i int) T

	bt.Iterable[T]
	bt.Traversable[T]
}

type MutList[T any] interface {
	List[T]
	Mut

	Put(i int, v T)
	Append(v T)
	Delete(i int)
}

//

type SyncList[T any] interface {
	List[T]
	Sync
}

type SyncMutList[T any] interface {
	MutList[T]
	Sync
}

//

type Set[T any] interface {
	Len() int
	Contains(v T) bool

	bt.Iterable[T]
	bt.Traversable[T]
}

type MutSet[T any] interface {
	Set[T]
	Mut

	Add(v T)
	TryAdd(v T) bool
	Remove(v T)
	TryRemove(v T) bool
}

//

type Map[K, V any] interface {
	Len() int
	Contains(k K) bool
	Get(k K) V
	TryGet(k K) (V, bool)

	bt.Iterable[bt.Kv[K, V]]
	bt.Traversable[bt.Kv[K, V]]
}

type MutMap[K, V any] interface {
	Map[K, V]
	Mut

	Put(k K, v V)
	Delete(k K)
	Default(k K, v V) bool
}

//

type OrderedMap[K, V any] interface {
	Map[K, V]
	Ordered[bt.Kv[K, V]]
}

type MutOrderedMap[K, V any] interface {
	OrderedMap[K, V]
	MutMap[K, V]
}

//

type SyncMap[K, V any] interface {
	Map[K, V]
	Sync
}

type SyncMutMap[K, V any] interface {
	MutMap[K, V]
	Sync
}

//

type BiMap[K, V comparable] interface {
	Map[K, V]

	Invert() BiMap[V, K]
}

type MutBiMap[K, V comparable] interface {
	MutMap[K, V]
	BiMap[K, V]

	MutInvert() MutBiMap[V, K]
}

//

type PersistentMap[K, V any] interface {
	Map[K, V]
	Persistent[bt.Kv[K, V]]

	With(k K, v V) PersistentMap[K, V]
	Without(k K) PersistentMap[K, V]
	Default(k K, v V) PersistentMap[K, V]
}

//

type Decay[T any] interface {
	Mut

	Decay() T
}
