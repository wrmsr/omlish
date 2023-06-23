package marshal

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	rfl "github.com/wrmsr/bane/core/reflect"
)

type RegThing struct {
	I int
	S string
}

func TestRegistry(t *testing.T) {
	reg := NewRegistry(nil)

	reg.Register(rfl.TypeOf[RegThing](),
		SetType{Marshaler: NewFuncMarshaler(func(ctx *MarshalContext, rv reflect.Value) (Value, error) {
			return MakeString("reg_thing"), nil
		})})

	o := reg.m[rfl.TypeOf[RegThing]()].m[rfl.TypeOf[SetType]()][0]
	tu.AssertEqual(t, o != nil, true)

	rt := RegThing{I: 420, S: "four twenty"}
	mv := check.Must1(o.(SetType).Marshaler.Marshal(&MarshalContext{}, reflect.ValueOf(rt)))
	fmt.Println(mv)
}
