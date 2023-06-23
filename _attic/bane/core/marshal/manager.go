package marshal

import (
	"reflect"

	ctr "github.com/wrmsr/bane/core/container"
	its "github.com/wrmsr/bane/core/iterators"
	rfl "github.com/wrmsr/bane/core/reflect"
	stu "github.com/wrmsr/bane/core/structs"
)

//

type Manager struct {
	sic *stu.StructInfoCache

	reg *Registry

	mf MarshalerFactory
	uf UnmarshalerFactory
}

func (m *Manager) MarshalRfl(rv reflect.Value, o ...MarshalOpt) (Value, error) {
	ty := rv.Type()
	mc := MarshalContext{
		Make: m.mf.Make,
		Opts: ctr.NewStdMap(its.MakeTypeKvs(its.OfSlice(o))),
		Reg:  m.reg,
	}
	mi, err := m.mf.Make(&mc, ty)
	if err != nil {
		return nil, err
	}
	return mi.Marshal(&mc, rv)
}

func (m *Manager) Marshal(v any, o ...MarshalOpt) (Value, error) {
	return m.MarshalRfl(reflect.ValueOf(v), o...)
}

func (m *Manager) UnmarshalRfl(mv Value, ty reflect.Type, o ...UnmarshalOpt) (reflect.Value, error) {
	uc := UnmarshalContext{
		Make: m.uf.Make,
		Opts: ctr.NewStdMap(its.MakeTypeKvs(its.OfSlice(o))),
		Reg:  m.reg,
	}
	ui, err := m.uf.Make(&uc, ty)
	if err != nil {
		return rfl.Invalid(), err
	}
	return ui.Unmarshal(&uc, mv)
}

func (m *Manager) Unmarshal(mv Value, v any, o ...UnmarshalOpt) error {
	rv := reflect.ValueOf(v).Elem()
	uv, err := m.UnmarshalRfl(mv, rv.Type(), o...)
	if err != nil {
		return err
	}
	rv.Set(uv)
	return nil
}
