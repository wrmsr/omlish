package marshal

import (
	"encoding/base64"
	"reflect"

	rfl "github.com/wrmsr/bane/core/reflect"
)

///

type Base64Marshaler struct{}

var _ Marshaler = Base64Marshaler{}

func (m Base64Marshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	if rv.Type() != rfl.Bytes() {
		return nil, unhandledTypeOf(rv.Type())
	}

	if rv.IsNil() {
		return _nullValue, nil
	}

	return String{v: base64.StdEncoding.EncodeToString(rv.Bytes())}, nil
}

//

var base64MarshalerFactory = NewTypeMarshalerFactory(Base64Marshaler{}, rfl.TypeOf[[]byte]())

func NewBase64MarshalerFactory() MarshalerFactory {
	return base64MarshalerFactory
}

///

type Base64Unmarshaler struct{}

var _ Unmarshaler = Base64Unmarshaler{}

func (u Base64Unmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	switch mv := mv.(type) {

	case Null:
		return rfl.NilBytes(), nil

	case String:
		b, err := base64.StdEncoding.DecodeString(mv.v)
		if err != nil {
			return rfl.Invalid(), err
		}
		return reflect.ValueOf(b), nil

	}
	return rfl.Invalid(), unhandledTypeOf(reflect.TypeOf(mv))
}

//

var base64UnmarshalerFactory = NewTypeUnmarshalerFactory(Base64Unmarshaler{}, rfl.TypeOf[[]byte]())

func NewBase64UnmarshalerFactory() UnmarshalerFactory {
	return base64UnmarshalerFactory
}
