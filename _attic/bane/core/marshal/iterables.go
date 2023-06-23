package marshal

import (
	"reflect"

	its "github.com/wrmsr/bane/core/iterators"
)

///

type ReflectIterableMarshaler struct {
	m Marshaler

	h its.ReflectHelper
}

func NewReflectIterableMarshaler(m Marshaler) ReflectIterableMarshaler {
	return ReflectIterableMarshaler{m: m, h: its.NewReflectHelper()}
}

var _ Marshaler = ReflectIterableMarshaler{}

func (m ReflectIterableMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	if rv.IsNil() {
		return _nullValue, nil
	}

	var vs []Value
	var err error
	m.h.ForEach(rv, func(ev reflect.Value) bool {
		var mv Value
		mv, err = m.m.Marshal(ctx, ev)
		if err != nil {
			return false
		}

		vs = append(vs, mv)
		return true
	})
	if err != nil {
		return nil, err
	}
	return Array{v: vs}, nil
}

//

type AnyIterableMarshaler struct {
	m Marshaler
}

func NewAnyIterableMarshaler(m Marshaler) AnyIterableMarshaler {
	return AnyIterableMarshaler{m: m}
}

var _ Marshaler = AnyIterableMarshaler{}

func (m AnyIterableMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	it := rv.Interface().(its.AnyIterable)

	var vs []Value
	for it := it.AnyIterate(); it.HasNext(); {
		e := it.Next()
		mv, err := m.m.Marshal(ctx, reflect.ValueOf(e))
		if err != nil {
			return nil, err
		}
		vs = append(vs, mv)
	}
	return Array{v: vs}, nil
}
