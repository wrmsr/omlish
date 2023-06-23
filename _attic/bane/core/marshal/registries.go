package marshal

import (
	"reflect"
	"sync"

	rfl "github.com/wrmsr/bane/core/reflect"
)

///

type RegistryItem interface {
	isRegistryItem()
}

//

type typeRegistry struct {
	ty reflect.Type
	s  []RegistryItem
	m  map[reflect.Type][]RegistryItem
}

type Registry struct {
	mtx sync.Mutex
	m   map[reflect.Type]*typeRegistry
	ps  []*Registry
}

func NewRegistry(parents []*Registry) *Registry {
	return &Registry{
		m: make(map[reflect.Type]*typeRegistry),

		ps: parents,
	}
}

func (r *Registry) Register(ty reflect.Type, items ...RegistryItem) *Registry {
	r.mtx.Lock()
	defer r.mtx.Unlock()

	ti := r.m[ty]
	if ti == nil {
		ti = &typeRegistry{
			ty: ty,
			m:  make(map[reflect.Type][]RegistryItem),
		}
		r.m[ty] = ti
	}

	so := len(ti.s)
	s := make([]RegistryItem, so+len(items))
	copy(s, ti.s)
	copy(s[so:], items)
	ti.s = s

	cm := make(map[reflect.Type]int)
	for _, e := range items {
		ity := reflect.TypeOf(e)
		cm[ity] = cm[ity] + 1
	}
	for ity, c := range cm {
		s0 := ti.m[ity]
		s1 := make([]RegistryItem, len(s0), len(s0)+c)
		copy(s1, s0)
		ti.m[ity] = s1
	}
	for _, e := range items {
		ity := reflect.TypeOf(e)
		ti.m[ity] = append(ti.m[ity], e)
	}

	return r
}

func (r *Registry) Get(ty reflect.Type) (ret []RegistryItem) {
	r.mtx.Lock()
	e := r.m[ty]
	if e != nil {
		ret = e.s
	}
	r.mtx.Unlock()
	return
}

func (r *Registry) GetOf(ty, ity reflect.Type) (ret []RegistryItem) {
	r.mtx.Lock()
	e := r.m[ty]
	if e != nil {
		ret = e.m[ity]
	}
	r.mtx.Unlock()
	return
}

///

type SetType struct {
	Marshaler   Marshaler
	Unmarshaler Unmarshaler

	MarshalerFactory   MarshalerFactory
	UnmarshalerFactory UnmarshalerFactory
}

func (ri SetType) isRegistryItem() {}

//

type RegistryMarshalerFactory struct{}

func NewRegistryMarshalerFactory() RegistryMarshalerFactory {
	return RegistryMarshalerFactory{}
}

var _ MarshalerFactory = RegistryMarshalerFactory{}

var _setTypeTy = rfl.TypeOf[SetType]()

func (f RegistryMarshalerFactory) Make(ctx *MarshalContext, a reflect.Type) (Marshaler, error) {
	if ctx.Reg == nil {
		return nil, nil
	}
	sts := ctx.Reg.GetOf(a, _setTypeTy)
	for i := len(sts) - 1; i >= 0; i-- {
		st := sts[i].(SetType)
		if st.MarshalerFactory != nil {
			return st.MarshalerFactory.Make(ctx, a)
		}
		if st.Marshaler != nil {
			return st.Marshaler, nil
		}
	}
	return nil, nil
}

//

type RegistryUnmarshalerFactory struct{}

func NewRegistryUnmarshalerFactory() RegistryUnmarshalerFactory {
	return RegistryUnmarshalerFactory{}
}

var _ UnmarshalerFactory = RegistryUnmarshalerFactory{}

func (f RegistryUnmarshalerFactory) Make(ctx *UnmarshalContext, a reflect.Type) (Unmarshaler, error) {
	if ctx.Reg == nil {
		return nil, nil
	}
	sts := ctx.Reg.GetOf(a, _setTypeTy)
	for i := len(sts) - 1; i >= 0; i-- {
		st := sts[i].(SetType)
		if st.UnmarshalerFactory != nil {
			return st.UnmarshalerFactory.Make(ctx, a)
		}
		if st.Unmarshaler != nil {
			return st.Unmarshaler, nil
		}
	}
	return nil, nil
}
