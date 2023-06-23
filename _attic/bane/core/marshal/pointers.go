package marshal

import (
	"reflect"

	rfl "github.com/wrmsr/bane/core/reflect"
)

///

type PointerMarshaler struct {
	elem Marshaler
}

func NewPointerMarshaler(elem Marshaler) PointerMarshaler {
	return PointerMarshaler{elem: elem}
}

var _ Marshaler = PointerMarshaler{}

func (m PointerMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	if rv.IsNil() {
		return _nullValue, nil
	}

	return m.elem.Marshal(ctx, rv.Elem())
}

//

var pointerMarshalerFactory = NewFuncFactory(func(ctx *MarshalContext, ty reflect.Type) (Marshaler, error) {
	if ty.Kind() != reflect.Pointer {
		return nil, nil
	}

	elem, err := ctx.Make(ctx, ty.Elem())
	if err != nil {
		return nil, err
	}
	return NewPointerMarshaler(elem), nil
})

func NewPointerMarshalerFactory() MarshalerFactory {
	return pointerMarshalerFactory
}

///

type PointerUnmarshaler struct {
	ty   reflect.Type
	elem Unmarshaler

	nv reflect.Value
}

func NewPointerUnmarshaler(ty reflect.Type, elem Unmarshaler) PointerUnmarshaler {
	return PointerUnmarshaler{ty: ty, elem: elem, nv: rfl.ZeroFor(ty)}
}

var _ Unmarshaler = PointerUnmarshaler{}

func (u PointerUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	switch mv := mv.(type) {

	case Null:
		return u.nv, nil

	default:
		ev, err := u.elem.Unmarshal(ctx, mv)
		if err != nil {
			return rfl.Invalid(), err
		}
		if ev.CanAddr() {
			return ev.Addr(), nil
		}
		pv := reflect.New(u.ty.Elem())
		pv.Elem().Set(ev)
		return pv, nil

	}
}

//

var pointerUnmarshalerFactory = NewFuncFactory(func(ctx *UnmarshalContext, ty reflect.Type) (Unmarshaler, error) {
	if ty.Kind() != reflect.Pointer {
		return nil, nil
	}

	elem, err := ctx.Make(ctx, ty.Elem())
	if err != nil {
		return nil, err
	}
	return NewPointerUnmarshaler(ty, elem), nil
})

func NewPointerUnmarshalerFactory() UnmarshalerFactory {
	return pointerUnmarshalerFactory
}
