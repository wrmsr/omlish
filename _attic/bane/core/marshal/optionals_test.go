package marshal

import (
	"encoding/json"
	"fmt"
	"reflect"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	rfl "github.com/wrmsr/bane/core/reflect"
	bt "github.com/wrmsr/bane/core/types"
)

//

func TestOptionals(t *testing.T) {
	m := NewOptionalMarshaler(rfl.TypeOf[bt.Optional[int]](), PrimitiveMarshaler{})
	u := NewOptionalUnmarshaler(rfl.TypeOf[bt.Optional[int]](), NewConvertUnmarshaler(rfl.TypeOf[int](), PrimitiveUnmarshaler{}))

	for _, v := range []bt.Optional[int]{
		bt.Just(10),
		bt.None[int](),
	} {
		mv := check.Must1(m.Marshal(&MarshalContext{}, reflect.ValueOf(v)))
		v2 := check.Must1(u.Unmarshal(&UnmarshalContext{}, mv)).Interface().(bt.Optional[int])
		tu.AssertDeepEqual(t, v, v2)
	}
}

func TestOptionalsFactory(t *testing.T) {
	m := check.Must1(
		optionalMarshalerFactory.Make(
			&MarshalContext{
				Make: NewPrimitiveMarshalerFactory().Make,
			},
			rfl.TypeOf[bt.Optional[int]](),
		),
	)

	u := check.Must1(
		optionalUnmarshalerFactory.Make(
			&UnmarshalContext{
				Make: NewConvertPrimitiveUnmarshalerFactory().Make,
			},
			rfl.TypeOf[bt.Optional[int]](),
		),
	)

	for _, v := range []bt.Optional[int]{
		bt.Just(10),
		bt.None[int](),
	} {
		mv := check.Must1(m.Marshal(&MarshalContext{}, reflect.ValueOf(v)))
		v2 := check.Must1(u.Unmarshal(&UnmarshalContext{}, mv)).Interface().(bt.Optional[int])
		tu.AssertDeepEqual(t, v, v2)
	}
}

//

type withOptInt struct {
	I bt.Optional[int]
}

type optInt0 = bt.Optional[int]

type withOptInt0 struct {
	I optInt0
}

type optInt1 bt.Optional[int]

type withOptInt1 struct {
	I optInt1
}

func TestTypeAliasOptional(t *testing.T) {
	for _, v := range []any{
		withOptInt{},
		withOptInt0{},
		withOptInt1{},
	} {
		m := check.Must1(Marshal(v))
		j := string(check.Must1(json.Marshal(m)))
		fmt.Println(j)
	}
}

//

type someOptIface interface {
	isSomeOptIface()
}

type someOptIfaceA struct{}
type someOptIfaceB struct{}

func (s someOptIfaceA) isSomeOptIface() {}
func (s someOptIfaceB) isSomeOptIface() {}

var _ = RegisterTo[someOptIface](
	SetImplOf[someOptIfaceA]("a"),
	SetImplOf[someOptIfaceB]("b"),
)

type withOptIface struct {
	O bt.Optional[someOptIface]
}

func TestOptionalInterface(t *testing.T) {
	for _, v := range []any{
		withOptIface{},
		withOptIface{O: bt.Just[someOptIface](someOptIfaceA{})},
		withOptIface{O: bt.Just[someOptIface](someOptIfaceB{})},
	} {
		m := check.Must1(Marshal(v))
		j := string(check.Must1(json.Marshal(m)))
		fmt.Println(j)
	}
}
