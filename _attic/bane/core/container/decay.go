package container

func DecayList[T any](l MutList[T]) List[T] {
	if l, ok := l.(Decay[List[T]]); ok {
		return l.Decay()
	}
	return NewSliceList[T](l)
}

func DecaySet[T comparable](l MutSet[T]) Set[T] {
	if l, ok := l.(Decay[Set[T]]); ok {
		return l.Decay()
	}
	return NewStdSet[T](l)
}

func DecayMap[K comparable, V any](l MutMap[K, V]) Map[K, V] {
	if l, ok := l.(Decay[Map[K, V]]); ok {
		return l.Decay()
	}
	return NewStdMap[K, V](l)
}
