package atomic

import (
	"sync/atomic"
)

type Value[T any] struct {
	v atomic.Value
}

func (v *Value[T]) Load() (val T) {
	if o := v.v.Load(); o != nil {
		return o.(T)
	}
	var z T
	return z
}

func (v *Value[T]) Store(val T) {
	v.v.Store(val)
}

func (v *Value[T]) Swap(new T) (old any) {
	return v.v.Swap(new).(T)
}
