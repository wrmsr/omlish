package marshal

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/wrmsr/bane/core/check"
	rfl "github.com/wrmsr/bane/core/reflect"
	stu "github.com/wrmsr/bane/core/structs"
)

type PolyI interface{ isPolyI() }

type PolyA struct{ I int }
type PolyB struct{ S string }
type PolyC struct{ L, R PolyI }

func (p PolyA) isPolyI() {}
func (p PolyB) isPolyI() {}
func (p PolyC) isPolyI() {}

func TestPolymorphism(t *testing.T) {
	i := PolyC{
		L: PolyA{
			I: 420,
		},
		R: PolyC{
			L: PolyA{
				I: 421,
			},
			R: PolyB{
				S: "four twenty three",
			},
		},
	}

	p := NewPolymorphism(
		rfl.TypeOf[PolyI](),
		[]SetImpl{
			{Impl: rfl.TypeOf[PolyA](), Tag: "a"},
			{Impl: rfl.TypeOf[PolyB](), Tag: "b"},
			{Impl: rfl.TypeOf[PolyC](), Tag: "c"},
		},
		nil,
	)

	sic := stu.NewStructInfoCache()

	mf := NewTypeCacheMarshalerFactory(NewRecursiveMarshalerFactory(NewCompositeMarshalerFactory(
		FirstComposite,
		NewPolymorphismMarshalerFactory(p),
		NewStructMarshalerFactory(sic),
		NewPrimitiveMarshalerFactory(),
	)))

	uf := NewTypeCacheUnmarshalerFactory(NewRecursiveUnmarshalerFactory(NewCompositeUnmarshalerFactory(
		FirstComposite,
		NewPolymorphismUnmarshalerFactory(p),
		NewStructUnmarshalerFactory(sic),
		NewConvertPrimitiveUnmarshalerFactory(),
	)))

	m := check.Must1(mf.Make(&MarshalContext{Make: mf.Make}, rfl.TypeOf[PolyI]()))
	u := check.Must1(uf.Make(&UnmarshalContext{Make: uf.Make}, rfl.TypeOf[PolyI]()))

	v := check.Must1(m.Marshal(&MarshalContext{}, reflect.ValueOf(i)))
	fmt.Println(v)

	o2 := check.Must1(u.Unmarshal(&UnmarshalContext{}, v))
	fmt.Println(o2)

	//tu.AssertDeepEqual(t, i, o2)
}

func TestRegistryPolymorphism(t *testing.T) {
	var o PolyI = PolyC{
		L: PolyA{
			I: 420,
		},
		R: PolyC{
			L: PolyA{
				I: 421,
			},
			R: PolyB{
				S: "four twenty three",
			},
		},
	}

	r := NewRegistry(nil)
	r.Register(rfl.TypeOf[PolyI](),
		SetImpl{Impl: rfl.TypeOf[PolyA](), Tag: "a"},
		SetImpl{Impl: rfl.TypeOf[PolyB](), Tag: "b"},
		SetImpl{Impl: rfl.TypeOf[PolyC](), Tag: "c"},
	)

	sic := stu.NewStructInfoCache()

	mf := NewTypeCacheMarshalerFactory(NewRecursiveMarshalerFactory(NewCompositeMarshalerFactory(
		FirstComposite,
		NewRegistryPolymorphismMarshalerFactory(),
		NewStructMarshalerFactory(sic),
		NewPrimitiveMarshalerFactory(),
	)))

	uf := NewTypeCacheUnmarshalerFactory(NewRecursiveUnmarshalerFactory(NewCompositeUnmarshalerFactory(
		FirstComposite,
		NewRegistryPolymorphismUnmarshalerFactory(),
		NewStructUnmarshalerFactory(sic),
		NewConvertPrimitiveUnmarshalerFactory(),
	)))

	mc := &MarshalContext{Make: mf.Make, Reg: r}
	uc := &UnmarshalContext{Make: uf.Make, Reg: r}

	m := check.Must1(mf.Make(mc, rfl.TypeOf[PolyI]()))
	u := check.Must1(uf.Make(uc, rfl.TypeOf[PolyI]()))

	v := check.Must1(m.Marshal(&MarshalContext{}, reflect.ValueOf(o)))
	fmt.Println(v)

	o2 := check.Must1(u.Unmarshal(&UnmarshalContext{}, v))
	fmt.Println(o2)
}
