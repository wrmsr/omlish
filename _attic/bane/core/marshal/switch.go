package marshal

import (
	"reflect"

	rfl "github.com/wrmsr/bane/core/reflect"
	bt "github.com/wrmsr/bane/core/types"
)

//

type MarshalPredicate = func(ctx *MarshalContext, rv reflect.Value) bool

func TrueMarshalPredicate(ctx *MarshalContext, rv reflect.Value) bool {
	return true
}

func PredicatedMarshaler(fn MarshalPredicate, m Marshaler) bt.Pair[MarshalPredicate, Marshaler] {
	return bt.PairOf(fn, m)
}

type SwitchMarshaler struct {
	s []bt.Pair[MarshalPredicate, Marshaler]
}

func NewSwitchMarshaler(s ...bt.Pair[MarshalPredicate, Marshaler]) SwitchMarshaler {
	return SwitchMarshaler{s: s}
}

var _ Marshaler = SwitchMarshaler{}

func (m SwitchMarshaler) Marshal(ctx *MarshalContext, rv reflect.Value) (Value, error) {
	for _, e := range m.s {
		if e.L(ctx, rv) {
			return e.R.Marshal(ctx, rv)
		}
	}
	return nil, unhandledTypeOf(rv.Type())
}

//

type UnmarshalPredicate = func(ctx *UnmarshalContext, mv Value) bool

func TrueUnmarshalPredicate(ctx *UnmarshalContext, mv Value) bool {
	return true
}

func PredicatedUnmarshaler(fn UnmarshalPredicate, u Unmarshaler) bt.Pair[UnmarshalPredicate, Unmarshaler] {
	return bt.PairOf(fn, u)
}

type SwitchUnmarshaler struct {
	s []bt.Pair[UnmarshalPredicate, Unmarshaler]
}

func NewSwitchUnmarshaler(s ...bt.Pair[UnmarshalPredicate, Unmarshaler]) SwitchUnmarshaler {
	return SwitchUnmarshaler{s: s}
}

var _ Unmarshaler = SwitchUnmarshaler{}

func (m SwitchUnmarshaler) Unmarshal(ctx *UnmarshalContext, mv Value) (reflect.Value, error) {
	for _, e := range m.s {
		if e.L(ctx, mv) {
			return e.R.Unmarshal(ctx, mv)
		}
	}
	return rfl.Invalid(), unhandledTypeOf(reflect.TypeOf(mv))
}
