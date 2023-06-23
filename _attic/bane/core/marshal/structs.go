package marshal

import (
	"errors"
	"reflect"

	rfl "github.com/wrmsr/bane/core/reflect"
	stu "github.com/wrmsr/bane/core/structs"
	bt "github.com/wrmsr/bane/core/types"
)

///

type SetField struct {
	Name string
	Tag  string

	Omit bool

	Marshaler   Marshaler
	Unmarshaler Unmarshaler
}

func (ri SetField) Coalesce(sfs ...SetField) SetField {
	for _, sf := range sfs {
		ri.Name = bt.Coalesce(sf.Name, ri.Name)
		ri.Tag = bt.Coalesce(sf.Tag, ri.Tag)
		ri.Omit = bt.Coalesce(sf.Omit, ri.Omit)
		if sf.Marshaler != nil {
			ri.Marshaler = sf.Marshaler
		}
		if sf.Unmarshaler != nil {
			ri.Unmarshaler = sf.Unmarshaler
		}
	}
	return ri
}

func (ri SetField) isRegistryItem() {}

///

func NewStructFieldGetter(fi *stu.FieldInfo) ObjectFieldGetter {
	return func(ctx *MarshalContext, rv reflect.Value) (bt.Optional[reflect.Value], error) {
		fv, ok := fi.GetValue(rv)
		if !ok {
			return bt.None[reflect.Value](), nil
		}
		return bt.Just(fv), nil
	}
}

//

type StructMarshalerFactory struct {
	sic *stu.StructInfoCache
}

func NewStructMarshalerFactory(sic *stu.StructInfoCache) StructMarshalerFactory {
	return StructMarshalerFactory{sic: sic}
}

var _ MarshalerFactory = StructMarshalerFactory{}

var _setFieldTy = rfl.TypeOf[SetField]()

func collectStructSetFields(r *Registry, ty reflect.Type) map[string]SetField {
	if r == nil {
		return nil
	}
	s := r.GetOf(ty, _setFieldTy)
	if len(s) < 1 {
		return nil
	}
	m := make(map[string]SetField)
	for _, sfi := range s {
		sf := sfi.(SetField)
		m[sf.Name] = m[sf.Name].Coalesce(sf)
	}
	return m
}

func (mf StructMarshalerFactory) Make(ctx *MarshalContext, ty reflect.Type) (Marshaler, error) {
	if ty.Kind() != reflect.Struct {
		return nil, nil
	}

	si := mf.sic.Info(ty)
	fsfs := collectStructSetFields(ctx.Reg, ty)
	var flds []ObjectMarshalerField
	var err error
	si.Fields().Flat().ForEach(func(fi *stu.FieldInfo) bool {
		var sf SetField
		if fsfs != nil {
			sf = fsfs[fi.Name().String()]
		}
		var tag = fi.Name().String()
		if sf.Tag != "" {
			tag = sf.Tag
		}
		if sf.Omit {
			return true
		}
		var impl = sf.Marshaler
		if impl == nil {
			impl, err = ctx.Make(ctx, fi.Type())
			if err != nil {
				return false
			}
		}
		of := ObjectMarshalerField{
			Name: tag,
			Get:  NewStructFieldGetter(fi),
			Impl: impl,
		}
		flds = append(flds, of)
		return true
	})
	if err != nil {
		return nil, err
	}
	return NewObjectMarshaler(flds...), nil
}

///

func NewStructFactory(si *stu.StructInfo) ObjectFactory {
	return func(ctx *UnmarshalContext) reflect.Value {
		return reflect.New(si.Type()).Elem()
	}
}

func NewStructFieldSetter(fi *stu.FieldInfo) ObjectFieldSetter {
	return func(ctx *UnmarshalContext, ov, fv reflect.Value) error {
		if !fi.SetValue(ov.Addr().Interface(), fv.Interface()) {
			return errors.New("can't set struct value")
		}
		return nil
	}
}

//

type StructUnmarshalerFactory struct {
	sic *stu.StructInfoCache
}

func NewStructUnmarshalerFactory(sic *stu.StructInfoCache) StructUnmarshalerFactory {
	return StructUnmarshalerFactory{sic: sic}
}

var _ UnmarshalerFactory = StructUnmarshalerFactory{}

func (mf StructUnmarshalerFactory) Make(ctx *UnmarshalContext, ty reflect.Type) (Unmarshaler, error) {
	if ty.Kind() != reflect.Struct {
		return nil, nil
	}

	si := mf.sic.Info(ty)
	fsfs := collectStructSetFields(ctx.Reg, ty)
	var flds []ObjectUnmarshalerField
	var err error
	si.Fields().Flat().ForEach(func(fi *stu.FieldInfo) bool {
		var sf SetField
		if fsfs != nil {
			sf = fsfs[fi.Name().String()]
		}
		var tag = fi.Name().String()
		if sf.Tag != "" {
			tag = sf.Tag
		}
		if sf.Omit {
			return true
		}
		var impl = sf.Unmarshaler
		impl, err = ctx.Make(ctx, fi.Type())
		if err != nil {
			return false
		}
		of := ObjectUnmarshalerField{
			Name: tag,
			Set:  NewStructFieldSetter(fi),
			Impl: impl,
		}
		flds = append(flds, of)
		return true
	})
	if err != nil {
		return nil, err
	}
	fac := NewStructFactory(si)
	return NewObjectUnmarshaler(fac, flds...), nil
}
