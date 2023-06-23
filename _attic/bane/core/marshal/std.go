package marshal

import (
	"encoding"
	"fmt"
	"reflect"

	rfl "github.com/wrmsr/bane/core/reflect"
)

///

type StdTextMarshaler struct{}

var _ Marshaler = StdTextMarshaler{}

func (m StdTextMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	if rfl.SafeIsNil(rv) {
		return _nullValue, nil
	}
	tm := rv.Interface().(encoding.TextMarshaler)
	b, err := tm.MarshalText()
	if err != nil {
		return nil, err
	}
	return String{v: string(b)}, nil
}

//

var stdTextMarshalerTy = rfl.TypeOf[encoding.TextMarshaler]()

var stdTextMarshalerFactory = NewFuncFactory(func(ctx *MarshalContext, ty reflect.Type) (Marshaler, error) {
	if !ty.AssignableTo(stdTextMarshalerTy) {
		return nil, nil
	}
	return StdTextMarshaler{}, nil
})

func NewStdTextMarshalerFactory() MarshalerFactory {
	return stdTextMarshalerFactory
}

///

type StdTextUnmarshaler struct {
	ty reflect.Type
}

func NewStdTextUnmarshaler(ty reflect.Type) Unmarshaler {
	if !reflect.PointerTo(ty).AssignableTo(stdTextUnmarshalerTy) {
		panic(fmt.Errorf("must be pointer-assignable to TextUnmarshaler"))
	}
	return StdTextUnmarshaler{ty: ty}
}

var _ Unmarshaler = StdTextUnmarshaler{}

func (u StdTextUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	var s string
	switch mv := mv.(type) {

	case Null:
		s = ""

	case String:
		s = mv.v

	default:
		return rfl.Invalid(), unhandledTypeOf(reflect.TypeOf(mv))
	}

	rv := reflect.New(u.ty)
	tu := rv.Interface().(encoding.TextUnmarshaler)
	if err := tu.UnmarshalText([]byte(s)); err != nil {
		return rfl.Invalid(), err
	}
	return rv.Elem(), nil
}

//

var stdTextUnmarshalerTy = rfl.TypeOf[encoding.TextUnmarshaler]()

func NewStdTextUnmarshalerFactory(ty reflect.Type) UnmarshalerFactory {
	return NewTypeUnmarshalerFactory(NewStdTextUnmarshaler(ty), ty)
}
