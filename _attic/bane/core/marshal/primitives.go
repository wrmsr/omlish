package marshal

import (
	"reflect"

	rfl "github.com/wrmsr/bane/core/reflect"
)

///

var primitiveTypes = map[reflect.Type]reflect.Type{
	rfl.TypeOf[bool]():    rfl.TypeOf[bool](),
	rfl.TypeOf[int]():     rfl.TypeOf[int64](),
	rfl.TypeOf[int8]():    rfl.TypeOf[int64](),
	rfl.TypeOf[int16]():   rfl.TypeOf[int64](),
	rfl.TypeOf[int32]():   rfl.TypeOf[int64](),
	rfl.TypeOf[int64]():   rfl.TypeOf[int64](),
	rfl.TypeOf[uint]():    rfl.TypeOf[uint64](),
	rfl.TypeOf[uint8]():   rfl.TypeOf[uint64](),
	rfl.TypeOf[uint16]():  rfl.TypeOf[uint64](),
	rfl.TypeOf[uint32]():  rfl.TypeOf[uint64](),
	rfl.TypeOf[uint64]():  rfl.TypeOf[uint64](),
	rfl.TypeOf[uintptr](): rfl.TypeOf[uint64](),
	rfl.TypeOf[float32](): rfl.TypeOf[float64](),
	rfl.TypeOf[float64](): rfl.TypeOf[float64](),
	rfl.TypeOf[string]():  rfl.TypeOf[string](),
}

var primitiveKinds = (func() map[reflect.Kind]reflect.Type {
	m := make(map[reflect.Kind]reflect.Type)
	for t := range primitiveTypes {
		m[t.Kind()] = t
	}
	return m
})()

//

type Primitive interface {
	isPrimitive()
}

func (v Bool) isPrimitive()   {}
func (v Int) isPrimitive()    {}
func (v Float) isPrimitive()  {}
func (v String) isPrimitive() {}

//.

type PrimitiveMarshaler struct{}

var _ Marshaler = PrimitiveMarshaler{}

func (p PrimitiveMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	switch rv.Kind() {

	case reflect.Bool:
		return Bool{v: rv.Bool()}, nil

	case
		reflect.Int,
		reflect.Int8,
		reflect.Int16,
		reflect.Int32,
		reflect.Int64:
		return Int{v: rv.Int()}, nil

	case
		reflect.Uint,
		reflect.Uint8,
		reflect.Uint16,
		reflect.Uint32,
		reflect.Uint64,
		reflect.Uintptr:
		return Int{v: int64(rv.Uint()), u: true}, nil

	case
		reflect.Float32,
		reflect.Float64:
		return Float{v: rv.Float()}, nil

	case reflect.String:
		return String{v: rv.String()}, nil

	}
	return nil, unhandledTypeOf(rv.Type())
}

//

var primitiveMarshalerFactory = func() MarshalerFactory {
	i := PrimitiveMarshaler{}
	m := make(map[reflect.Type]Marshaler, len(primitiveTypes))
	for ty := range primitiveTypes {
		m[ty] = i
	}
	return NewTypeMapMarshalerFactory(m)
}()

func NewPrimitiveMarshalerFactory() MarshalerFactory {
	return primitiveMarshalerFactory
}

///

type PrimitiveUnmarshaler struct{}

var _ Unmarshaler = PrimitiveUnmarshaler{}

func (p PrimitiveUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	switch mv := mv.(type) {

	case Bool:
		if mv.v {
			return rfl.True(), nil
		} else {
			return rfl.False(), nil
		}

	case Int:
		if mv.u {
			return reflect.ValueOf(uint64(mv.v)), nil
		} else {
			return reflect.ValueOf(mv.v), nil
		}

	case Float:
		return reflect.ValueOf(mv.v), nil

	case String:
		return reflect.ValueOf(mv.v), nil

	}
	return rfl.Invalid(), unhandledTypeOf(reflect.TypeOf(mv))
}

//

var primitiveUnmarshalerFactory = func() UnmarshalerFactory {
	i := PrimitiveUnmarshaler{}
	m := make(map[reflect.Type]Unmarshaler, len(primitiveTypes))
	for ty := range primitiveTypes {
		m[ty] = i
	}
	return NewTypeMapUnmarshalerFactory(m)
}()

func NewPrimitiveUnmarshalerFactory() UnmarshalerFactory {
	return primitiveUnmarshalerFactory
}
