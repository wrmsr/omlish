package marshal

import (
	"errors"
	"fmt"
	"reflect"
	"testing"

	"github.com/wrmsr/bane/core/check"
	tu "github.com/wrmsr/bane/core/dev/testing"
	ju "github.com/wrmsr/bane/core/json"
	stu "github.com/wrmsr/bane/core/structs"
	bt "github.com/wrmsr/bane/core/types"
)

type FooStruct struct {
	M map[bt.Optional[int]][]*string
	S string
}

func TestDefaultFactory(t *testing.T) {
	sic := stu.NewStructInfoCache()

	mf := NewTypeCacheMarshalerFactory(NewCompositeMarshalerFactory(
		FirstComposite,
		NewPrimitiveMarshalerFactory(),
		NewPointerMarshalerFactory(),
		NewIndexMarshalerFactory(),
		NewMapMarshalerFactory(),
		NewBase64MarshalerFactory(),
		NewTimeMarshalerFactory(DefaultTimeMarshalLayout),
		NewOptionalMarshalerFactory(),
		NewStructMarshalerFactory(sic),
	))

	uf := NewTypeCacheUnmarshalerFactory(NewCompositeUnmarshalerFactory(
		FirstComposite,
		NewConvertPrimitiveUnmarshalerFactory(),
		NewPointerUnmarshalerFactory(),
		NewIndexUnmarshalerFactory(),
		NewMapUnmarshalerFactory(),
		NewBase64UnmarshalerFactory(),
		NewTimeUnmarshalerFactory(DefaultTimeUnmarshalLayouts()),
		NewOptionalUnmarshalerFactory(),
		NewStructUnmarshalerFactory(sic),
	))

	o := FooStruct{
		M: map[bt.Optional[int]][]*string{
			bt.Just(10):    {bt.PtrTo("ten"), bt.PtrTo("one zero")},
			bt.Just(20):    {bt.PtrTo("twenty"), bt.PtrTo("two zero")},
			bt.None[int](): {bt.PtrTo("none")},
		},
		S: "foo..",
	}
	fmt.Println(o)

	for i := 0; i < 3; i++ {
		m := check.Must1(mf.Make(&MarshalContext{Make: mf.Make}, reflect.TypeOf(o)))
		u := check.Must1(uf.Make(&UnmarshalContext{Make: uf.Make}, reflect.TypeOf(o)))

		v := check.Must1(m.Marshal(&MarshalContext{}, reflect.ValueOf(o)))
		fmt.Println(v)

		o2 := check.Must1(u.Unmarshal(&UnmarshalContext{}, v))
		fmt.Println(o2)
	}
}

type tfca struct {
	I int
}

type tfcb struct {
	A tfca
	F float32
}

type tfcc struct {
	S string
}

type tfcd struct {
	B tfcb
	C tfcc
}

func TestFactoryCaching(t *testing.T) {
	sic := stu.NewStructInfoCache()

	mf := NewTypeCacheMarshalerFactory(NewCompositeMarshalerFactory(
		FirstComposite,
		NewPrimitiveMarshalerFactory(),
		NewPointerMarshalerFactory(),
		NewIndexMarshalerFactory(),
		NewMapMarshalerFactory(),
		NewBase64MarshalerFactory(),
		NewTimeMarshalerFactory(DefaultTimeMarshalLayout),
		NewOptionalMarshalerFactory(),
		NewStructMarshalerFactory(sic),
	))

	for i := 0; i < 2; i++ {
		for _, o := range []any{
			tfcb{},
			tfcd{},
		} {
			m := check.Must1(mf.Make(&MarshalContext{Make: mf.Make}, reflect.TypeOf(o)))

			v := check.Must1(m.Marshal(&MarshalContext{}, reflect.ValueOf(o)))
			fmt.Println(v)

			fmt.Println(ju.MarshalPretty(v))
		}
	}
}

type intOnlyMf struct{}

var _ MarshalerFactory = intOnlyMf{}

func (i intOnlyMf) Make(ctx *MarshalContext, ty reflect.Type) (Marshaler, error) {
	if ty == reflect.TypeOf(0) {
		return NewPrimitiveMarshalerFactory().Make(ctx, ty)
	}
	return nil, errors.New("no")
}

func TestTypCacheFactoryClearNmBug(t *testing.T) {
	mf := NewTypeCacheMarshalerFactory(intOnlyMf{})

	rv := reflect.ValueOf(420)

	m := check.Must1(mf.Make(&MarshalContext{}, rv.Type()))
	fmt.Println(check.Must1(ju.MarshalPretty(check.Must1(m.Marshal(&MarshalContext{}, rv)))))

	for i := 0; i < 3; i++ {
		rv = reflect.ValueOf("420")
		_, err := mf.Make(&MarshalContext{}, rv.Type())
		tu.AssertEqual(t, err != nil, true)
	}
}
