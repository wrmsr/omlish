package marshal

import (
	"reflect"

	ctr "github.com/wrmsr/bane/core/container"
)

///

type BaseContext interface {
	isBaseContext()
}

///

type MarshalOpt interface {
	isMarshalOpt()
}

type BaseMarshalOpt struct{}

func (o BaseMarshalOpt) isMarshalOpt() {}

//

type MarshalContext struct {
	Make func(ctx *MarshalContext, ty reflect.Type) (Marshaler, error)
	Opts ctr.Map[reflect.Type, MarshalOpt]
	Reg  *Registry
}

func (c *MarshalContext) isBaseContext() {}

type Marshaler interface {
	Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error)
}

//

type FuncMarshaler struct {
	fn func(ctx *MarshalContext, rv reflect.Value) (Value, error)
}

func NewFuncMarshaler(fn func(ctx *MarshalContext, rv reflect.Value) (Value, error)) FuncMarshaler {
	return FuncMarshaler{fn: fn}
}

var _ Marshaler = FuncMarshaler{}

func (m FuncMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	return m.fn(ctx, rv)
}

//

type MarshalerFactory = Factory[Marshaler, *MarshalContext, reflect.Type]

func NewFuncMarshalerFactory(fn func(ctx *MarshalContext, a reflect.Type) (Marshaler, error)) MarshalerFactory {
	return NewFuncFactory[Marshaler, *MarshalContext, reflect.Type](fn)
}

func NewTypeMapMarshalerFactory(m map[reflect.Type]Marshaler) MarshalerFactory {
	return NewTypeMapFactory[Marshaler, *MarshalContext](m)
}

func NewTypeMarshalerFactory(impl Marshaler, tys ...reflect.Type) MarshalerFactory {
	m := make(map[reflect.Type]Marshaler, len(tys))
	for _, ty := range tys {
		m[ty] = impl
	}
	return NewTypeMapMarshalerFactory(m)
}

func NewTypeCacheMarshalerFactory(f MarshalerFactory) MarshalerFactory {
	return NewTypeCacheFactory[Marshaler, *MarshalContext](f)
}

func NewRecursiveMarshalerFactory(f MarshalerFactory) MarshalerFactory {
	return NewRecursiveTypeFactory(f, func() (Marshaler, func(Marshaler)) {
		var m Marshaler
		return NewFuncMarshaler(func(ctx *MarshalContext, rv reflect.Value) (Value, error) {
				if m == nil {
					panic("recursive impl not yet set")
				}
				return m.Marshal(ctx, rv)
			}), func(m_ Marshaler) {
				m = m_
			}
	})
}

func NewCompositeMarshalerFactory(st CompositeStrategy, fs ...MarshalerFactory) MarshalerFactory {
	return NewCompositeFactory[Marshaler, *MarshalContext, reflect.Type](st, fs...)
}

///

type UnmarshalOpt interface {
	isUnmarshalOpt()
}

type BaseUnmarshalOpt struct{}

func (o BaseUnmarshalOpt) isUnmarshalOpt() {}

//

type UnmarshalContext struct {
	BaseContext

	Make func(ctx *UnmarshalContext, ty reflect.Type) (Unmarshaler, error)
	Opts ctr.Map[reflect.Type, UnmarshalOpt]
	Reg  *Registry
}

func (c *UnmarshalContext) isBaseContext() {}

type Unmarshaler interface {
	Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error)
}

//

type FuncUnmarshaler struct {
	fn func(ctx *UnmarshalContext, mv Value) (reflect.Value, error)
}

func NewFuncUnmarshaler(fn func(ctx *UnmarshalContext, mv Value) (reflect.Value, error)) FuncUnmarshaler {
	return FuncUnmarshaler{fn: fn}
}

var _ Unmarshaler = FuncUnmarshaler{}

func (u FuncUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	return u.fn(ctx, mv)
}

//

type UnmarshalerFactory = Factory[Unmarshaler, *UnmarshalContext, reflect.Type]

func NewFuncUnmarshalerFactory(fn func(ctx *UnmarshalContext, a reflect.Type) (Unmarshaler, error)) UnmarshalerFactory {
	return NewFuncFactory[Unmarshaler, *UnmarshalContext, reflect.Type](fn)
}

func NewTypeMapUnmarshalerFactory(m map[reflect.Type]Unmarshaler) UnmarshalerFactory {
	return NewTypeMapFactory[Unmarshaler, *UnmarshalContext](m)
}

func NewTypeUnmarshalerFactory(impl Unmarshaler, tys ...reflect.Type) UnmarshalerFactory {
	m := make(map[reflect.Type]Unmarshaler, len(tys))
	for _, ty := range tys {
		m[ty] = impl
	}
	return NewTypeMapUnmarshalerFactory(m)
}

func NewTypeCacheUnmarshalerFactory(f UnmarshalerFactory) UnmarshalerFactory {
	return NewTypeCacheFactory[Unmarshaler, *UnmarshalContext](f)
}

func NewRecursiveUnmarshalerFactory(f UnmarshalerFactory) UnmarshalerFactory {
	return NewRecursiveTypeFactory(f, func() (Unmarshaler, func(Unmarshaler)) {
		var u Unmarshaler
		return NewFuncUnmarshaler(func(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
				if u == nil {
					panic("recursive impl not yet set")
				}
				return u.Unmarshal(ctx, mv)
			}), func(u_ Unmarshaler) {
				u = u_
			}
	})
}

func NewCompositeUnmarshalerFactory(st CompositeStrategy, fs ...UnmarshalerFactory) UnmarshalerFactory {
	return NewCompositeFactory[Unmarshaler, *UnmarshalContext, reflect.Type](st, fs...)
}
