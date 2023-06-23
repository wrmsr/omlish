package marshal

import (
	"reflect"

	rfl "github.com/wrmsr/bane/core/reflect"
)

///

type ConvertMarshaler struct {
	ty    reflect.Type
	child Marshaler
}

func NewConvertMarshaler(ty reflect.Type, child Marshaler) ConvertMarshaler {
	return ConvertMarshaler{ty: ty, child: child}
}

var _ Marshaler = ConvertMarshaler{}

func (m ConvertMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	cv := rv.Convert(m.ty)
	mv, err := m.child.Marshal(ctx, cv)
	if err != nil {
		return nil, err
	}

	return mv, nil
}

//

func NewConvertUserPrimitiveMarshalerFactory() MarshalerFactory {
	return NewFuncMarshalerFactory(func(ctx *MarshalContext, a reflect.Type) (Marshaler, error) {
		p, ok := primitiveKinds[a.Kind()]
		if !ok {
			return nil, nil
		}
		m, err := ctx.Make(ctx, p)
		if err != nil {
			return nil, err
		}
		return NewConvertMarshaler(a, m), nil
	})
}

///

type ConvertUnmarshaler struct {
	ty    reflect.Type
	child Unmarshaler
}

func NewConvertUnmarshaler(ty reflect.Type, child Unmarshaler) ConvertUnmarshaler {
	return ConvertUnmarshaler{ty: ty, child: child}
}

var _ Unmarshaler = ConvertUnmarshaler{}

func (u ConvertUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	rv, err := u.child.Unmarshal(ctx, mv)
	if err != nil {
		return rfl.Invalid(), err
	}

	return rv.Convert(u.ty), nil
}

//

var convertPrimitiveUnmarshalerFactory = func() UnmarshalerFactory {
	m := make(map[reflect.Type]Unmarshaler, len(primitiveTypes))
	for ty, cty := range primitiveTypes {
		if ty != cty {
			m[ty] = NewConvertUnmarshaler(ty, PrimitiveUnmarshaler{})
		} else {
			m[ty] = PrimitiveUnmarshaler{}
		}
	}
	return NewTypeMapUnmarshalerFactory(m)
}()

func NewConvertPrimitiveUnmarshalerFactory() UnmarshalerFactory {
	return convertPrimitiveUnmarshalerFactory
}

//

func NewConvertUserPrimitiveUnmarshalerFactory() UnmarshalerFactory {
	return NewFuncUnmarshalerFactory(func(ctx *UnmarshalContext, a reflect.Type) (Unmarshaler, error) {
		p, ok := primitiveKinds[a.Kind()]
		if !ok {
			return nil, nil
		}
		m, err := ctx.Make(ctx, p)
		if err != nil {
			return nil, err
		}
		return NewConvertUnmarshaler(a, m), nil
	})
}
