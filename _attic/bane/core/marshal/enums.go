package marshal

import (
	"errors"
	"fmt"
	"reflect"

	"github.com/wrmsr/bane/core/maps"
	rfl "github.com/wrmsr/bane/core/reflect"
)

///

type EnumMarshaler[T comparable] struct {
	m map[T]Value
}

func NewEnumMarshaler[T comparable](m map[T]string) EnumMarshaler[T] {
	return EnumMarshaler[T]{m: maps.MapValues(func(s string) Value { return MakeString(s) }, m)}
}

var _ Marshaler = EnumMarshaler[int]{}

func (m EnumMarshaler[T]) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	iv := rv.Interface()
	it, ok := iv.(T)
	if !ok {
		return nil, unhandledTypeOf(rv.Type())
	}
	mv, ok := m.m[it]
	if !ok {
		return nil, errors.New("unknown enum value")
	}
	return mv, nil
}

//

type EnumUnmarshaler struct {
	m map[string]reflect.Value
}

func NewEnumUnmarshaler(m map[string]any) EnumUnmarshaler {
	return EnumUnmarshaler{m: maps.MapValues(reflect.ValueOf, m)}
}

var _ Unmarshaler = EnumUnmarshaler{}

func (u EnumUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	switch mv := mv.(type) {

	case String:
		s := mv.v
		v, ok := u.m[s]
		if !ok {
			return rfl.Invalid(), fmt.Errorf("unknown enum value: %s", s)
		}
		return v, nil

	}
	return rfl.Invalid(), unhandledTypeOf(reflect.TypeOf(mv))
}

///

func SetEnumTypes[T comparable](m map[T]string) SetType {
	i := make(map[string]any, len(m))
	for k, v := range m {
		i[v] = k
	}
	return SetType{
		Marshaler:   NewEnumMarshaler[T](m),
		Unmarshaler: NewEnumUnmarshaler(i),
	}
}

func SetStringerEnumTypes[T comparable](vs ...T) SetType {
	m := make(map[T]string, len(vs))
	for _, v := range vs {
		var o any
		o = v
		s := o.(fmt.Stringer).String()
		m[v] = s
	}
	return SetEnumTypes[T](m)
}
