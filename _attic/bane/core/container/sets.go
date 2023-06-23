package container

func Union[T comparable](ss ...Set[T]) Set[T] {
	r := NewMutStdSet[T](nil)
	for _, s := range ss {
		s.ForEach(func(v T) bool {
			r.Add(v)
			return true
		})
	}
	return r
}

func Intersection[T comparable](ss ...Set[T]) Set[T] {
	if len(ss) < 1 {
		return NewStdSet[T](nil)
	}
	cts := make(map[T]int)
	for _, s := range ss[1:] {
		s.ForEach(func(v T) bool {
			cts[v] = cts[v] + 1
			return true
		})
	}
	r := NewMutStdSet[T](nil)
	for v, ct := range cts {
		if ct == len(ss) {
			r.Add(v)
		}
	}
	return r
}

func Difference[T comparable](ss ...Set[T]) Set[T] {
	if len(ss) < 1 {
		return NewStdSet[T](nil)
	}
	r := NewMutStdSet[T](ss[0])
	for _, s := range ss[1:] {
		s.ForEach(func(v T) bool {
			r.Remove(v)
			return true
		})
	}
	return r
}

func SetPop[T comparable](s MutSet[T]) (T, bool) {
	if s.Len() < 1 {
		var z T
		return z, false
	}
	var r T
	s.ForEach(func(v T) bool {
		r = v
		return false
	})
	s.Remove(r)
	return r, true
}
