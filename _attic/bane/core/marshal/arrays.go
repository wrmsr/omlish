package marshal

import (
	"fmt"
	"reflect"

	"github.com/wrmsr/bane/core/check"
	rfl "github.com/wrmsr/bane/core/reflect"
)

///

type IndexMarshaler struct {
	elem Marshaler
}

func NewIndexMarshaler(elem Marshaler) IndexMarshaler {
	return IndexMarshaler{elem: elem}
}

var _ Marshaler = IndexMarshaler{}

func (m IndexMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	if rv.Kind() == reflect.Slice && rv.IsNil() {
		return _nullValue, nil
	}

	l := rv.Len()
	vs := make([]Value, l)
	for i := 0; i < l; i++ {
		v, err := m.elem.Marshal(ctx, rv.Index(i))
		if err != nil {
			return nil, err
		}
		vs[i] = v
	}
	return Array{v: vs}, nil
}

//

var indexMarshalerFactory = NewFuncFactory(func(ctx *MarshalContext, ty reflect.Type) (Marshaler, error) {
	if ty.Kind() != reflect.Slice && ty.Kind() != reflect.Array {
		return nil, nil
	}

	elem, err := ctx.Make(ctx, ty.Elem())
	if err != nil {
		return nil, err
	}
	return NewIndexMarshaler(elem), nil
})

func NewIndexMarshalerFactory() MarshalerFactory {
	return indexMarshalerFactory
}

///

type SliceUnmarshaler struct {
	ty   reflect.Type
	elem Unmarshaler

	nv reflect.Value
}

func NewSliceUnmarshaler(ty reflect.Type, elem Unmarshaler) SliceUnmarshaler {
	check.Equal(ty.Kind(), reflect.Slice)
	return SliceUnmarshaler{ty: ty, elem: elem, nv: rfl.ZeroFor(ty)}
}

var _ Unmarshaler = SliceUnmarshaler{}

func indexUnmarshal(mv Array, rv reflect.Value, u Unmarshaler, ctx *UnmarshalContext) error {
	for i, em := range mv.v {
		er, err := u.Unmarshal(ctx, em)
		if err != nil {
			return err
		}
		rv.Index(i).Set(er)
	}
	return nil
}

func (u SliceUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	switch mv := mv.(type) {

	case Null:
		return u.nv, nil

	case Array:
		l := len(mv.v)
		rv := reflect.MakeSlice(u.ty, l, l)
		if err := indexUnmarshal(mv, rv, u.elem, ctx); err != nil {
			return rfl.Invalid(), err
		}
		return rv, nil

	}
	return rfl.Invalid(), unhandledType()
}

//

type ArrayUnmarshaler struct {
	ty   reflect.Type
	elem Unmarshaler

	l int
}

func NewArrayUnmarshaler(ty reflect.Type, elem Unmarshaler) ArrayUnmarshaler {
	check.Equal(ty.Kind(), reflect.Array)
	return ArrayUnmarshaler{ty: ty, elem: elem, l: ty.Len()}
}

var _ Unmarshaler = ArrayUnmarshaler{}

func (u ArrayUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	switch mv := mv.(type) {

	case Array:
		l := len(mv.v)
		if l != u.l {
			return rfl.Invalid(), fmt.Errorf("array length mismatch: got %d need %d", l, u.l)
		}
		rv := reflect.New(u.ty).Elem()
		if err := indexUnmarshal(mv, rv, u.elem, ctx); err != nil {
			return rfl.Invalid(), err
		}
		return rv, nil

	}
	return rfl.Invalid(), unhandledTypeOf(reflect.TypeOf(mv))
}

//

var indexUnmarshalerFactory = NewFuncFactory(func(ctx *UnmarshalContext, ty reflect.Type) (Unmarshaler, error) {
	if ty.Kind() != reflect.Slice && ty.Kind() != reflect.Array {
		return nil, nil
	}

	elem, err := ctx.Make(ctx, ty.Elem())
	if err != nil {
		return nil, err
	}
	if ty.Kind() == reflect.Slice {
		return NewSliceUnmarshaler(ty, elem), nil
	} else {
		return NewArrayUnmarshaler(ty, elem), nil
	}
})

func NewIndexUnmarshalerFactory() UnmarshalerFactory {
	return indexUnmarshalerFactory
}
