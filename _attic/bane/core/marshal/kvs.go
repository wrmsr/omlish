package marshal

import (
	"reflect"

	its "github.com/wrmsr/bane/core/iterators"
	bt "github.com/wrmsr/bane/core/types"
)

///

type ReflectKvIterableMarshaler struct {
	k Marshaler
	v Marshaler

	h its.ReflectHelper
}

func NewReflectKvIterableMarshaler(k, v Marshaler) ReflectKvIterableMarshaler {
	return ReflectKvIterableMarshaler{k: k, v: v, h: its.NewReflectHelper()}
}

var _ Marshaler = ReflectKvIterableMarshaler{}

func (m ReflectKvIterableMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	if rv.IsNil() {
		return _nullValue, nil
	}

	var vs []bt.Kv[Value, Value]
	var err error
	m.h.ForEach(rv, func(ev reflect.Value) bool {
		kv := ev.Interface().(bt.AnyKv)

		var k Value
		k, err = m.k.Marshal(ctx, reflect.ValueOf(kv.AnyK()))
		if err != nil {
			return false
		}

		var v Value
		v, err = m.v.Marshal(ctx, reflect.ValueOf(kv.AnyV()))
		if err != nil {
			return false
		}

		vs = append(vs, bt.KvOf(k, v))
		return true
	})
	if err != nil {
		return nil, err
	}
	return Object{v: vs}, nil
}

///

type AnyKvIterableMarshaler struct {
	k Marshaler
	v Marshaler
}

func NewAnyKvIterableMarshaler(k, v Marshaler) AnyKvIterableMarshaler {
	return AnyKvIterableMarshaler{k: k, v: v}
}

var _ Marshaler = AnyKvIterableMarshaler{}

func (m AnyKvIterableMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	ai := rv.Interface().(its.AnyIterable)

	var vs []bt.Kv[Value, Value]
	for ai := ai.AnyIterate(); ai.HasNext(); {
		kv := ai.Next().(bt.AnyKv)

		k, err := m.k.Marshal(ctx, reflect.ValueOf(kv.AnyK()))
		if err != nil {
			return nil, err
		}

		v, err := m.v.Marshal(ctx, reflect.ValueOf(kv.AnyV()))
		if err != nil {
			return nil, err
		}

		vs = append(vs, bt.KvOf(k, v))
	}
	return Object{v: vs}, nil
}
